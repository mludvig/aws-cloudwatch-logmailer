ALL := logmailer-cloudformation.yml

all: ${ALL}

clean:
	rm -f ${ALL}

logmailer-cloudformation.yml: logmailer-lambda.py util/logmailer-cloudformation.skeleton.yml
	./util/import-files.py --yaml $< > $@
