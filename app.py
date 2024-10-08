import pickle
import urllib.request
import uuid
import sqlite3
from datetime import datetime
from flask import Flask,render_template, jsonify, request

#Initializing the application 
app = Flask(__name__)


@app.route('/') # Decorate Charater (Empty Route)

def index(): 
   return render_template ("index.html")

@app.route('/results', methods = ["POST"])
def results():   
    aldyVoted = 0       

    public_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    unique_id = f"{public_ip}_{user_agent}"

    today = datetime.today().strftime('%Y-%m-%d')   
    cndidt = request.form.get('radioVote')
    
    akd = 1 if cndidt == 'akd' else 0
    dj = 1 if cndidt =='dj' else 0
    nr = 1 if cndidt == 'nr' else 0
    rw = 1 if cndidt == 'rw' else 0
    sf = 1 if cndidt == 'sw' else 0
    sp = 1 if cndidt == 'sp' else 0
    

    con = sqlite3.connect('election.db')
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS vote
               (ip text PRIMARY KEY, vote_date text, rw real, nr real, sp real, akd real, sf real, dj real)
                ''')
    

    # Check if the IP has already voted
    cur.execute('SELECT * FROM vote WHERE ip = ?', (unique_id,))
    existing_vote = cur.fetchone()

    if existing_vote:
        aldyVoted = 1
    else:    
        cur.execute('''INSERT INTO vote (ip, vote_date, rw, nr, sp, akd, sf, dj) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (unique_id, today, rw, nr, sp, akd, sf, dj))
        con.commit()
    

    cur.execute('''SELECT 
                  SUM(rw) as sum_rw, 
                  SUM(nr) as sum_nr, 
                  SUM(sp) as sum_sp, 
                  SUM(akd) as sum_akd, 
                  SUM(sf) as sum_sf, 
                  SUM(dj) as sum_dj
               FROM vote''')

    row = cur.fetchone()
    con.close() 

    sum_rw = row[0] if row[0] is not None else 0
    sum_nr = row[1] if row[1] is not None else 0
    sum_sp = row[2] if row[2] is not None else 0
    sum_akd = row[3] if row[3] is not None else 0
    sum_sf = row[4] if row[4] is not None else 0
    sum_dj = row[5] if row[5] is not None else 0

    totol_votes = sum_rw + sum_nr + sum_sp + sum_akd + sum_sf + sum_dj

    if totol_votes > 0:
        pct_rw = sum_rw / totol_votes * 100
        pct_nr = sum_nr / totol_votes * 100
        pct_sp = sum_sp / totol_votes * 100
        pct_akd = sum_akd / totol_votes * 100
        pct_sf = sum_sf / totol_votes * 100
        pct_dj = sum_dj / totol_votes * 100
    else:
        pct_rw = pct_nr = pct_sp = pct_akd = pct_sf = pct_dj = 0



    return render_template('results.html', 
                           sum_rw = sum_rw,
                           sum_nr = sum_nr,
                           sum_sp = sum_sp,
                           sum_akd = sum_akd,
                           sum_sf = sum_sf,
                           sum_dj = sum_dj,
                           totol_votes = round(totol_votes,0),
                           pct_rw = round(pct_rw,1),
                           pct_nr = round(pct_nr,1),
                           pct_sp = round(pct_sp,1),
                           pct_akd = round(pct_akd,1),
                           pct_sf = round(pct_sf,1),
                           pct_dj = round(pct_dj,1),
                           aldyVoted = aldyVoted,
                           slctd_cndidt = cndidt)

    #return jsonify({"message": f"Your Mac ID : {mac_id, aldyVoted }"})

if __name__ == '__main__':
    app.run( debug=True)
