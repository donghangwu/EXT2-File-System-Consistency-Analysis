# NAME: Donghang Wu, Tristan Que
# ID: 605346965, 505379744
# EMAIL: dwu20@g.ucla.edu, tristanq816@gmail.com
default:
	rm -f lab3b lab3b-605346965.tar.gz
	ln buildpy.sh lab3b
	chmod +x lab3b
dist:
	tar -czvf lab3b-605346965.tar.gz lab3b.py buildpy.sh Makefile README 
clean:
	rm -f lab3b lab3b-605346965.tar.gz

	