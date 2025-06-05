from BEE.BEE import BEE

app = BEE()

@app.route("/")
@app.route("/home")
def home():
	return "Welcome to BEE!"

@app.route("/user/<URL_param>", methods=["GET"])
def user_profile(URL_param):
	return f"URL_param: {URL_param}"

if __name__ == "__main__":
	app.run()
