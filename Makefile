fmt:
	docker run --rm -v `pwd`:/src kiwicom/black:20.8b1 black /src -l 79
	docker run --rm -v `pwd`:/src alphachai/isort:latest -m 3 --tc /src
