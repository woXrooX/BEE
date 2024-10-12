from BEE.BEE import BEE

app = BEE()

@app.route('/')
def home(): return "Welcome to BEE!"

@app.route('/about')
def about(): return "About BEE"

@app.route('/user/<username>/settings')
def user_profile(username):
	return f"<h1>user > {username} > settings</h1>"
