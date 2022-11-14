
from loguru import logger
import sqlite3
from typing import Optional, Tuple

from .. import __database_name__

def CreateSQLWikiFeetConnection(database_name : str) -> Optional[sqlite3.Connection]:
    Conn : Optional[sqlite3.Connection] = None
    try:
        Conn = sqlite3.connect(database_name)
        Conn.cursor().execute("CREATE TABLE IF NOT EXISTS filecaptions (id INTEGER PRIMARY KEY, f_name TEXT NOT NULL, caption TEXT NOT NULL, user_name TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        return Conn
    except sqlite3.Error as e:
        logger.exception(e)

def GetCaption( FileName) -> Optional[str]:
    """Ettii taulusta kuvan nimen perusteella sen captionin"""
    connection = CreateSQLWikiFeetConnection(__database_name__)    
    if connection is None:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, caption, user_name, timestamp FROM filecaptions WHERE f_name=?",(FileName,))
        rows = cursor.fetchall()
        logger.info("Return : {}",rows[0])
        if len(rows) > 0:
            return f"#{rows[0][0]} | {rows[0][1]}\n~{rows[0][2]} – {rows[0][3]}"
    except sqlite3.OperationalError as e:
        logger.error("Tiedostonimellä : {}, ei ollut kuvatekstiä",FileName)
        logger.exception(e)
    finally:
        connection.close()
        
def GetFileForID(ID : int) -> Optional[Tuple[str, str]]:
    connection = CreateSQLWikiFeetConnection(__database_name__)    
    if connection is None:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT f_name FROM filecaptions WHERE id=?",(ID,))
        rows = cursor.fetchall()
        logger.info("Return : {}",rows[0])
        if len(rows) > 0:
            return rows[0][0]
    except sqlite3.OperationalError as e:
        logger.error("ID:llä : {}, ei ollut kuvaa",ID)
        logger.exception(e)
    finally:
        connection.close()

def DeleteRowFromDatabase(ID : int) -> bool:
    connection = CreateSQLWikiFeetConnection(__database_name__)    
    if connection is None:
        return None
    
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM filecaptions WHERE id=?",(ID,))
        connection.commit()
    except sqlite3.OperationalError as e:
        logger.error("ID:llä : {}, ei ollut kuvaa",ID)
        logger.exception(e)
    finally:
        connection.close()

def AddCaption( FileName, Caption, UserName) -> bool:
    """Lisää tietokantaan uuden rivin tiedostonimellä ja sen captionilla"""
    connection = CreateSQLWikiFeetConnection(__database_name__)    
    if connection is None:
        return False
    
    cursor = connection.cursor()

    cursor.execute("INSERT INTO filecaptions(f_name, caption, user_name) VALUES(?,?,?)", (FileName, Caption, UserName))
    
    logger.info("Tiedostonimellä {}, lisätty kuvateksti '{}', käyttäjänimeltä : {}", FileName, Caption, UserName)

    connection.commit()
    connection.close()
    return True