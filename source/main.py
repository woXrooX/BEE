from BEE.BEE import Core

app = Core()

@app.route("/")
def home(): return "Welcome to BEE!"

@app.route("/about")
def about(): return "About BEE"

@app.route("/user/<URL_param>", methods=["GET"])
def user_profile(URL_param):
	return f"URL_param: {URL_param}"
