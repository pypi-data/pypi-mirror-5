JAVA_FOLDER="java"
JAVA_SRC=$JAVA_FOLDER/src
JAVA_BIN=$JAVA_FOLDER/bin
JAVA_LIB=$JAVA_FOLDER/lib
mkdir -p $JAVA_BIN

PY4J_JAR="/usr/local/share/py4j/py4j0.7.jar"
JAVA_CLASS=.:$PY4J_JAR

for filename in `ls $JAVA_LIB`;
do
	JAVA_CLASS=$JAVA_CLASS:$JAVA_LIB/$filename
done

javac -d $JAVA_BIN -cp $JAVA_CLASS $JAVA_SRC/omnilab/bd/chenxm/DetectRightEntry.java

java -cp $JAVA_BIN:$JAVA_CLASS omnilab.bd.chenxm.DetectRightEntry
