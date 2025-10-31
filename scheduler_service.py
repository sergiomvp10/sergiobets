#!/usr/bin/env python3
"""
Scheduler Service for SergioBets - 24/7 Automated Prediction Scheduling
Runs on Render to send predictions at scheduled times to premium users
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from dotenv import load_dotenv

from footystats_api import obtener_partidos_del_dia
from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia
from telegram_utils import enviar_telegram_masivo

load_dotenv()

TIMEZONE = os.getenv('TIMEZONE', 'America/Phoenix')
MORNING_SEND_TIME = os.getenv('MORNING_SEND_TIME', '06:59')
MORNING_MAX = int(os.getenv('MORNING_MAX', '3'))
MORNING_SPACING_SECONDS = int(os.getenv('MORNING_SPACING_SECONDS', '120'))
PREMATCH_HOURS_BEFORE = int(os.getenv('PREMATCH_HOURS_BEFORE', '2'))
DATABASE_URL = os.getenv('DATABASE_URL')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TZ = ZoneInfo(TIMEZONE)

class PredictionScheduler:
    def __init__(self):
        self.db_url = DATABASE_URL
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        jobstores = {'default': SQLAlchemyJobStore(url=self.db_url)}
        executors = {'default': ThreadPoolExecutor(10)}
        job_defaults = {'coalesce': False, 'max_instances': 3}
        
        self.scheduler = BlockingScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=TZ
        )
        logger.info(f"Scheduler initialized with timezone: {TIMEZONE}")
    
    def get_db_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def ensure_table_exists(self):
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_notifications (
                    id SERIAL PRIMARY KEY,
                    match_id VARCHAR(255) NOT NULL,
                    notify_type VARCHAR(20) NOT NULL CHECK (notify_type IN ('morning', 'prematch')),
                    scheduled_at TIMESTAMPTZ NOT NULL,
                    sent_at TIMESTAMPTZ,
                    kickoff_utc TIMESTAMPTZ NOT NULL,
                    home_team VARCHAR(255),
                    away_team VARCHAR(255),
                    league VARCHAR(255),
                    prediction_data JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(match_id, notify_type)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_scheduled_at ON scheduled_notifications(scheduled_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_sent_at ON scheduled_notifications(sent_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_notifications_notify_type ON scheduled_notifications(notify_type)")
            conn.commit()
            cur.close()
            conn.close()
            logger.info("✅ Database table ensured")
        except Exception as e:
            logger.error(f"❌ Error ensuring table exists: {e}")
            raise
    
    def convert_unix_to_datetime(self, unix_timestamp: int) -> datetime:
        dt_utc = datetime.fromtimestamp(unix_timestamp, tz=ZoneInfo('UTC'))
        return dt_utc.astimezone(TZ)
    
    def is_already_scheduled(self, match_id: str, notify_type: str) -> bool:
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM scheduled_notifications WHERE match_id = %s AND notify_type = %s", (str(match_id), notify_type))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"❌ Error checking if scheduled: {e}")
            return False
    
    def mark_as_scheduled(self, match_id: str, notify_type: str, scheduled_at: datetime,
                         kickoff_utc: datetime, home_team: str, away_team: str,
                         league: str, prediction_data: Optional[Dict] = None):
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            import json
            prediction_json = json.dumps(prediction_data) if prediction_data else None
            cur.execute("""
                INSERT INTO scheduled_notifications 
                (match_id, notify_type, scheduled_at, kickoff_utc, home_team, away_team, league, prediction_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id, notify_type) DO UPDATE
                SET scheduled_at = EXCLUDED.scheduled_at, kickoff_utc = EXCLUDED.kickoff_utc, prediction_data = EXCLUDED.prediction_data
            """, (str(match_id), notify_type, scheduled_at, kickoff_utc, home_team, away_team, league, prediction_json))
            conn.commit()
            cur.close()
            conn.close()
            logger.info(f"✅ Marked as scheduled: {match_id} ({notify_type})")
        except Exception as e:
            logger.error(f"❌ Error marking as scheduled: {e}")
    
    def mark_as_sent(self, match_id: str, notify_type: str):
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE scheduled_notifications SET sent_at = NOW() WHERE match_id = %s AND notify_type = %s AND sent_at IS NULL", (str(match_id), notify_type))
            conn.commit()
            cur.close()
            conn.close()
            logger.info(f"✅ Marked as sent: {match_id} ({notify_type})")
        except Exception as e:
            logger.error(f"❌ Error marking as sent: {e}")
    
    def send_single_prediction(self, prediction: Dict[str, Any], match_id: str, notify_type: str):
        try:
            logger.info(f"📤 Sending {notify_type} prediction for match {match_id}...")
            fecha = datetime.now(TZ).strftime('%Y-%m-%d')
            mensaje = generar_mensaje_ia([prediction], fecha)
            result = enviar_telegram_masivo(mensaje=mensaje, token=TELEGRAM_BOT_TOKEN, bot_username="BetGeniuXbot", only_premium=True)
            if result.get('exito'):
                logger.info(f"✅ Sent to {result.get('enviados_exitosos', 0)} premium users")
                self.mark_as_sent(match_id, notify_type)
            else:
                logger.error(f"❌ Failed to send: {result.get('error', 'Unknown error')}")
        except Exception as e:
            logger.error(f"❌ Error sending prediction: {e}", exc_info=True)
    
    def send_morning_predictions(self):
        logger.info("🌅 Starting morning predictions job...")
        try:
            now_local = datetime.now(TZ)
            date_str = now_local.strftime('%Y-%m-%d')
            partidos = obtener_partidos_del_dia(fecha=date_str, use_cache=False)
            if not partidos:
                logger.warning("⚠️ No matches found for today")
                return
            
            matches_with_time = []
            for match in partidos:
                try:
                    unix_time = match.get('date_unix')
                    if not unix_time:
                        continue
                    kickoff_local = self.convert_unix_to_datetime(unix_time)
                    kickoff_utc = datetime.fromtimestamp(unix_time, tz=ZoneInfo('UTC'))
                    formatted_match = {
                        'id': match.get('id'),
                        'hora': kickoff_local.strftime('%H:%M'),
                        'liga': match.get('competition_name', 'Unknown'),
                        'local': match.get('home_name', 'Home'),
                        'visitante': match.get('away_name', 'Away'),
                        'cuotas': {
                            'local': str(match.get('odds_ft_1', '2.0')),
                            'empate': str(match.get('odds_ft_x', '3.0')),
                            'visitante': str(match.get('odds_ft_2', '3.0'))
                        },
                        'kickoff_local': kickoff_local,
                        'kickoff_utc': kickoff_utc
                    }
                    matches_with_time.append(formatted_match)
                except Exception as e:
                    logger.warning(f"⚠️ Error processing match: {e}")
                    continue
            
            if not matches_with_time:
                logger.warning("⚠️ No valid matches")
                return
            
            predictions = filtrar_apuestas_inteligentes(matches_with_time, opcion_numero=1)
            predictions_sorted = sorted(predictions, key=lambda x: (
                next((m['kickoff_local'] for m in matches_with_time if m['id'] == x.get('id')), datetime.now(TZ)),
                -x.get('confianza', 0)
            ))
            morning_picks = predictions_sorted[:MORNING_MAX]
            
            for i, prediction in enumerate(morning_picks):
                match_id = prediction.get('id', f"unknown_{i}")
                if self.is_already_scheduled(match_id, 'morning'):
                    continue
                send_time = now_local + timedelta(seconds=i * MORNING_SPACING_SECONDS)
                orig_match = next((m for m in matches_with_time if m['id'] == match_id), None)
                if not orig_match:
                    continue
                
                self.mark_as_scheduled(match_id=match_id, notify_type='morning',
                    scheduled_at=send_time.astimezone(ZoneInfo('UTC')), kickoff_utc=orig_match['kickoff_utc'],
                    home_team=orig_match['local'], away_team=orig_match['visitante'],
                    league=orig_match['liga'], prediction_data=prediction)
                
                self.scheduler.add_job(func=self.send_single_prediction, trigger='date', run_date=send_time,
                    args=[prediction, match_id, 'morning'], id=f"morning_{match_id}_{i}", replace_existing=True)
                logger.info(f"📅 Scheduled morning prediction {i+1}/{len(morning_picks)} at {send_time.strftime('%H:%M')}")
            
            logger.info(f"✅ Morning job completed: {len(morning_picks)} scheduled")
        except Exception as e:
            logger.error(f"❌ Error in morning job: {e}", exc_info=True)
    
    def schedule_prematch_predictions(self):
        logger.info("📋 Scheduling prematch predictions...")
        try:
            now_local = datetime.now(TZ)
            date_str = now_local.strftime('%Y-%m-%d')
            partidos = obtener_partidos_del_dia(fecha=date_str, use_cache=False)
            if not partidos:
                logger.warning("⚠️ No matches for prematch")
                return
            
            morning_match_ids = set()
            try:
                conn = self.get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT match_id FROM scheduled_notifications WHERE notify_type = 'morning' AND DATE(kickoff_utc) = %s", (date_str,))
                morning_match_ids = {row['match_id'] for row in cur.fetchall()}
                cur.close()
                conn.close()
            except Exception as e:
                logger.warning(f"⚠️ Error getting morning IDs: {e}")
            
            scheduled_count = 0
            for match in partidos:
                try:
                    match_id = str(match.get('id'))
                    if match_id in morning_match_ids or self.is_already_scheduled(match_id, 'prematch'):
                        continue
                    unix_time = match.get('date_unix')
                    if not unix_time:
                        continue
                    kickoff_local = self.convert_unix_to_datetime(unix_time)
                    kickoff_utc = datetime.fromtimestamp(unix_time, tz=ZoneInfo('UTC'))
                    send_time_local = kickoff_local - timedelta(hours=PREMATCH_HOURS_BEFORE)
                    if send_time_local <= now_local:
                        continue
                    
                    formatted_match = {
                        'id': match_id, 'hora': kickoff_local.strftime('%H:%M'),
                        'liga': match.get('competition_name', 'Unknown'),
                        'local': match.get('home_name', 'Home'), 'visitante': match.get('away_name', 'Away'),
                        'cuotas': {'local': str(match.get('odds_ft_1', '2.0')), 'empate': str(match.get('odds_ft_x', '3.0')), 'visitante': str(match.get('odds_ft_2', '3.0'))}
                    }
                    
                    self.mark_as_scheduled(match_id=match_id, notify_type='prematch',
                        scheduled_at=send_time_local.astimezone(ZoneInfo('UTC')), kickoff_utc=kickoff_utc,
                        home_team=match.get('home_name', ''), away_team=match.get('away_name', ''),
                        league=match.get('competition_name', ''))
                    
                    self.scheduler.add_job(func=self.send_prematch_prediction, trigger='date', run_date=send_time_local,
                        args=[formatted_match, match_id], id=f"prematch_{match_id}", replace_existing=True)
                    scheduled_count += 1
                    logger.info(f"📅 Scheduled prematch for {match_id} at {send_time_local.strftime('%H:%M')}")
                except Exception as e:
                    logger.warning(f"⚠️ Error scheduling match: {e}")
                    continue
            logger.info(f"✅ Prematch scheduling completed: {scheduled_count} scheduled")
        except Exception as e:
            logger.error(f"❌ Error in prematch scheduling: {e}", exc_info=True)
    
    def send_prematch_prediction(self, match: Dict[str, Any], match_id: str):
        try:
            logger.info(f"📤 Sending prematch for {match_id}...")
            predictions = filtrar_apuestas_inteligentes([match], opcion_numero=1)
            if not predictions:
                logger.warning(f"⚠️ No prediction for {match_id}")
                return
            fecha = datetime.now(TZ).strftime('%Y-%m-%d')
            mensaje = generar_mensaje_ia(predictions, fecha)
            result = enviar_telegram_masivo(mensaje=mensaje, token=TELEGRAM_BOT_TOKEN, bot_username="BetGeniuXbot", only_premium=True)
            if result.get('exito'):
                logger.info(f"✅ Sent to {result.get('enviados_exitosos', 0)} premium users")
                self.mark_as_sent(match_id, 'prematch')
            else:
                logger.error(f"❌ Failed to send: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Error sending prematch: {e}", exc_info=True)
    
    def start(self):
        try:
            logger.info("🚀 Starting Prediction Scheduler Service...")
            logger.info(f"⏰ Timezone: {TIMEZONE}")
            logger.info(f"🌅 Morning: {MORNING_SEND_TIME}")
            logger.info(f"📊 Morning max: {MORNING_MAX}")
            logger.info(f"⏱️ Spacing: {MORNING_SPACING_SECONDS}s")
            logger.info(f"⏰ Prematch hours: {PREMATCH_HOURS_BEFORE}h")
            self.ensure_table_exists()
            hour, minute = map(int, MORNING_SEND_TIME.split(':'))
            self.scheduler.add_job(func=self.send_morning_predictions, trigger='cron', hour=hour, minute=minute,
                timezone=TZ, id='morning_predictions', replace_existing=True)
            logger.info(f"✅ Scheduled morning job at {MORNING_SEND_TIME} {TIMEZONE}")
            self.scheduler.add_job(func=self.schedule_prematch_predictions, trigger='cron', hour=0, minute=5,
                timezone=TZ, id='prematch_scheduling', replace_existing=True)
            logger.info(f"✅ Scheduled prematch job at 00:05 {TIMEZONE}")
            logger.info("🔄 Running initial prematch scheduling...")
            self.schedule_prematch_predictions()
            logger.info("✅ Scheduler started!")
            logger.info("📋 Scheduled jobs:")
            try:
                for job in self.scheduler.get_jobs():
                    next_run = getattr(job, 'next_run_time', 'N/A')
                    logger.info(f"  - {job.id}: {next_run}")
            except Exception as e:
                logger.warning(f"Could not list job details: {e}")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("👋 Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error starting: {e}", exc_info=True)
            raise

def main():
    try:
        scheduler = PredictionScheduler()
        scheduler.start()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
