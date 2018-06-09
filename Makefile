ALL := logmailer-cloudformation.yml

all: ${ALL}

clean:
	rm -f ${ALL}

logmailer-cloudformation.yml: util/logmailer-cloudformation.skeleton.yml logmailer-lambda.py
	./util/import-files.py --yaml $< > $@
