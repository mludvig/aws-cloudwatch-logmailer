ALL := logmailer-cloudformation.yml tester-cloudformation.yml

all: ${ALL}

clean:
	rm -f ${ALL}

logmailer-cloudformation.yml: util/logmailer-cloudformation.skeleton.yml logmailer-lambda.py
	./util/import-files.py --yaml $< > $@

tester-cloudformation.yml: util/tester-cloudformation.skeleton.yml tester-lambda.py
	./util/import-files.py --yaml $< > $@
