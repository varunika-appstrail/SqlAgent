from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import markdown
from Agent.state_graph import graph
from Database import DatabaseConnect
from langchain_core.messages import HumanMessage


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!' 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        db_type = request.form.get('dbtype')
        uname = request.form.get('uname')
        passw = request.form.get('pass')
        hname = request.form.get('hname')
        pno = request.form.get('pno')
        
        session['db_type'] = db_type
        session['uname'] = uname
        session['passw'] = passw         
        session['hname'] = hname
        session['pno'] = pno

        try:
            d  = DatabaseConnect.DatabaseConnection(username=session['uname'],password=session['passw'],hostname=session['hname'],port=session['pno'],dialect=session['db_type'])
            if session['db_type']=='mysql':
             result = d.execute_query(query="SHOW DATABASES", database_name="")
            if session['db_type']=='postgresql':
             result = d.execute_query(query="SELECT datname FROM pg_database WHERE datistemplate = false;", database_name="defaultdb")
            if result:  
                return redirect(url_for('success'))  
        except Exception as e:
            flash(f"Database connection failed: {str(e)}", 'error')
            print(e)

    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

socketio = SocketIO(app, cors_allowed_origins="*")
@socketio.on("send_message")
def handle_message(data):
    user_message = data.get("message", "")
    state = {"messages": [HumanMessage(content=user_message)]}
 
    try:
        output_message = graph.invoke(state)
        response = output_message["messages"][-1].content
       
        response_html = markdown.markdown(response, extensions=["extra"])
    except Exception as e:
        response_html = f"<p>An error occurred: {e}</p>"
 
    emit("receive_message", {"message": response_html})
 
 
if __name__ == "__main__":
    socketio.run(app, debug=True)

