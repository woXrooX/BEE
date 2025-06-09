from BEE import BEE, session, Response

Bee = BEE()

@Bee.route("/")
@Bee.route("/home")
def home(request):
	print(request.get_JSON())
	return "Welcome to BEE!"

@Bee.route("/user/<URL_param>", methods=["GET"])
def user_profile(URL_param): return f"URL_param: {URL_param}"

@Bee.route("/log_in/<PWD>", methods=["GET"])
def log_in_PWD(PWD):
	if PWD == "JEFF":
		session["user"] = {
			"username": "My_name_is_JEFF",
			"id": 12345
		}

		return f"Logged in: {session}"

	else: return f"Invalid PWD"

@Bee.route("/visit")
def visit(request):
	count = session["user"].get("count", 0) + 1
	session["user"]["count"] = count
	return f"Visits: {session}"


if __name__ == "__main__": Bee.run()
