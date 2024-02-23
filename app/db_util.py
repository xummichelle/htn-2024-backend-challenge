import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

class MyDatabase():
    def __init__(self, db=os.getenv("DB_NAME"), 
                 host=os.getenv("HOST_NAME"), 
                 user=os.getenv("POSTGRES_USERNAME"), 
                 password=os.getenv("POSTGRES_PASSWORD")):
        self.conn = psycopg2.connect(database=db, host=host,user=user,password=password)
        self.cur = self.conn.cursor()

    def query(self, query):
        self.cur.execute(query)
        try:
            return json.dumps(self.cur.fetchone()[0])
        except:
            return None

    def update(self,query):
        self.cur.execute(query)
        self.cur.execute("commit;")

    def get_data(self,id=None):
        l_query = "select json_agg(data) from users";
        if id:
            l_query += f" where id={id};"
        return self.query(l_query)

    def update_info(self,id,new_data):
        l_query = f"update users set data = '{new_data}' where id={id};"
        self.update(l_query)

    def get_skills_data(self,max,min=0):
        l_query = "with data as (select jsonb_array_elements(data['skills']) s from users),"\
                f" a as (select s['skill'] skill,count(*) as counts from data group by s['skill']"
        if max:
            l_query += f" having count(*) between {min} and {max})"
        else:
            l_query += f" having count(*) > {min})"
        l_query += f" select json_agg(json_build_object('skill',a.skill,'count',a.counts)) from a;"
        return self.query(l_query)
        

    def close(self):
        self.cur.close()
        self.conn.close()

def exclude_keys(d, exclude_keys):
    return {k: d[k] for k in set(d.keys()) - set(exclude_keys)}

def update_or_insert(current_data, enter_data):
    current_data = json.loads(current_data)

    ## all key value except skills
    exclude_keys_list = ['skills']
    l_enter_data_without_skills = exclude_keys(enter_data, exclude_keys_list)
    for key in l_enter_data_without_skills:
        current_data[key] = l_enter_data_without_skills[key]

    ## for skills
    c_skills = current_data['skills']
    n_skills = enter_data['skills'] if 'skills' in enter_data else []
    for n_entry in n_skills:
        for c_entry in c_skills:
            if c_entry['skill'] == n_entry['skill']:
                c_entry['rating'] = n_entry['rating']
                break
        else:
            c_skills.append(n_entry)

    current_data['skills'] = c_skills
    return json.dumps(current_data)

def main():
    db = MyDatabase()
    db.close()

if __name__=='__main__':
    main()
