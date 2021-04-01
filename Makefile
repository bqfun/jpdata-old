fmt:
	docker run --rm -v `pwd`:/src kiwicom/black:20.8b1 black -l 79 /src
	docker run --rm -v `pwd`:/src kiwicom/isort:5.7.0 isort -m 3 --tc /src
