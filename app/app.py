from flask import Flask,request
from dotenv import load_dotenv
import app.db_util as du

db = du.MyDatabase()

def create_app():
    app = Flask(__name__)

    @app.route("/users/",methods=['GET'])
    def get_users():
        return db.get_data()

    @app.route("/users/<int:id>",methods=['GET'])
    def get_user(id):
        return db.get_data(id)

    @app.route("/skills/",methods=['GET'])
    def get_skills_count():
        
        my_dict = request.args.to_dict(flat=True)
        max = my_dict['max_frequency']
        min = my_dict['min_frequency']
        return db.get_skills_data(max, min)

    @app.route("/users/<int:id>",methods =['PUT'])
    def update_user(id):
        data = request.json
        print(data)
        l_current_info = db.get_data(id)
        print(l_current_info)
        new_data = du.update_or_insert(l_current_info, data)
        db.update_info(id, new_data)
        return new_data


    return app

if __name__=='__main__':
    app =  create_app()
    app.run(debug =True)
    db.close()
