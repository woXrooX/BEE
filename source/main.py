from BEE import BEE, session, Response

Bee = BEE()

@Bee.route("/")
@Bee.route("/home")
def home(): return "Welcome to BEE!"

@Bee.route("/user/<URL_param>", methods=["GET"])
def user_profile(URL_param): return f"URL_param: {URL_param}"

@Bee.route("/visit")
def visit(request):
	count = session.get("count", 0) + 1
	session["count"] = count
	return Response.JSON({"visits": count})


if __name__ == "__main__": Bee.run()
