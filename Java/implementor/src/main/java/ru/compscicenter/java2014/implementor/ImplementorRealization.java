package ru.compscicenter.java2014.implementor;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Parameter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.HashSet;

import static java.nio.file.Files.createDirectories;

/**
 * Created by Roman Fedorov on 30.11.2014.
 */

public class ImplementorRealization implements Implementor {
    /** Output Directory.
     */
    private String outputDir;

    public final String getOutputDirectory() {
        return this.outputDir;
    }

    public ImplementorRealization(final String outputDirectory) {
        outputDir = outputDirectory;
    }

    private String createMethodImplementation(final Method method) {
        String methodImpl = "\t"
            + Modifier.toString(method.getModifiers()).replace("abstract", "")
            + " "
            + method.getReturnType().getCanonicalName() + " " + method.getName()
            + getStringOfParams(method.getParameters());
        String returnValue = "0";
        if (method.getReturnType().equals(void.class)) {
            returnValue = "";
        } else if (method.getReturnType().equals(boolean.class)) {
            returnValue = "true";
        } else if (!method.getReturnType().isPrimitive()) {
            returnValue = "null";
        }
        return methodImpl + "\t\t return " + returnValue + ";\n\t}\n";
    }

    private String getStringOfParams(final Parameter[] params) {
        String stringOfParams = "(";
        for (Parameter p : params) {
            stringOfParams += p.getType().getCanonicalName()
                + " " + p.getName() + ", ";
        }
        if (params.length == 0) {
            stringOfParams += "  ";
        }
        return stringOfParams
                    .substring(0, stringOfParams.length() - 2) + ") {\n";
    }

    private String createMethods(final Class classToImpl)
                                        throws ImplementorException {
        if (Modifier.isFinal(classToImpl.getModifiers())) {
            throw new ImplementorException("");
        }

        String outputFileContent = "public class "
                                    + classToImpl.getSimpleName() + "Impl ";
        outputFileContent += classToImpl.isInterface() ?
                "implements " : "extends ";
        outputFileContent += classToImpl.getName() + " {\n";

        HashSet<String> generatedMethods = new HashSet<String>();
        for (Class currentClass = classToImpl; currentClass != null;
                          currentClass = currentClass.getSuperclass()) {
            for (Method m: currentClass.getDeclaredMethods()) {
                if (Modifier.isAbstract(m.getModifiers())) {
                    generatedMethods.add(createMethodImplementation(m));
                }
            }
            for (Class c: currentClass.getInterfaces()) {
                for (Method m: c.getDeclaredMethods()) {
                    generatedMethods.add(createMethodImplementation(m));
                }
            }
        }

        for (String m : generatedMethods) {
            outputFileContent += m;
        }
        return outputFileContent + "}";
    }

    public String implementFromDirectory(final String directoryPath,
                     final String className) throws ImplementorException {
        try {
            URL classFileURL = Paths.get(directoryPath).toUri().toURL();
            ClassLoader classLoader =
                          new URLClassLoader( new URL [] { classFileURL });
            Class classToImpl = classLoader.loadClass(className);
            String packagePath = className.replace(".", "/");
            Path pathToImpl = Paths.get(this.getOutputDirectory()
                                        + "/" + packagePath + "Impl.java");
            createDirectories(pathToImpl.getParent());
            Files.createFile(pathToImpl);
            String packageString;
            try {
                packageString = "package "
                            + classToImpl.getPackage().getName() + ";\n\n";
            } catch (Exception e) {
                packageString = "";
            }
            Files.write(pathToImpl, packageString.getBytes(),
                                                StandardOpenOption.APPEND);
            Files.write(pathToImpl, createMethods(classToImpl).getBytes(),
                                                StandardOpenOption.APPEND);
        } catch (Exception e) {
            throw new ImplementorException(e.getMessage());
        }
        return className + "Impl";
    }

    public String implementFromStandardLibrary(final String className)
                                            throws ImplementorException {
        try {
            ClassLoader classLoader =
                            ImplementorRealization.class.getClassLoader();
            Class classToImpl = classLoader.loadClass(className);
            Path pathToImpl = Paths.get(this.getOutputDirectory(),
                                classToImpl.getSimpleName() + "Impl.java");
            Files.createFile(pathToImpl);
            Files.write(pathToImpl, createMethods(classToImpl).getBytes(),
                                                StandardOpenOption.APPEND);
            return classToImpl.getSimpleName() + "Impl";
        } catch (Exception e) {
            throw new ImplementorException(e.getMessage());
        }
    }
}
