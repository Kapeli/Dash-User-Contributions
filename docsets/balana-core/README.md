Balana (Core)
=======================

This is a docset for WSO2's Balana XACML implementation (core package)


## Instructions
* Download latest javadocset: https://github.com/Kapeli/javadocset
* git clone https://github.com/wso2/balana.git && cd balana
* git apply
```
diff --git a/pom.xml b/pom.xml
index 5e18607..7968e9c 100644
--- a/pom.xml
+++ b/pom.xml
@@ -132,6 +132,14 @@
                         </instructions>
                     </configuration>
                 </plugin>
+            <plugin>
+                <groupId>org.apache.maven.plugins</groupId>
+                <artifactId>maven-javadoc-plugin</artifactId>
+                <version>3.0.0-M1</version>
+                <configuration>
+                    <additionalparam>-Xdoclint:none</additionalparam>
+                </configuration>
+            </plugin>
                 <plugin>
                     <groupId>org.codehaus.mojo</groupId>
                     <artifactId>buildnumber-maven-plugin</artifactId>
```
* mvn javadoc:javadoc
* javadocset balana-core target/site/apidocs/

## Contact Info
  * Email: kyle@kyleolivo.com
  * GitHub: kyleolivo