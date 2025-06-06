from BEE import BEE, session

app = BEE()

@app.route("/")
@app.route("/home")
def home():
	return "Welcome to BEE!"

@app.route("/user/<URL_param>", methods=["GET"])
def user_profile(URL_param):
	return f"URL_param: {URL_param}"

@app.route("/visit")
def visit(request):
	count = request.session.get("count", 0) + 1
	request.session["count"] = count
	return Response.JSON({"visits": count})


if __name__ == "__main__":
	app.run()
