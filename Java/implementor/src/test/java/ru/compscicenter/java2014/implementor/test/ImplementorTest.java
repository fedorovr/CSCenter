package ru.compscicenter.java2014.implementor.test;

import org.testng.annotations.AfterTest;
import org.testng.annotations.Test;
import ru.compscicenter.java2014.implementor.Implementor;

import javax.tools.*;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.Modifier;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.fest.assertions.api.Assertions.assertThat;

@Test(timeOut = 5000L, sequential = true)
public class ImplementorTest {

    /** You need to put here your local directories path*/
    static final private String TESTS_DIRECTORY = "/example/directory";
    static final private String OUTPUT_DIRECTORY = "/example/directory";

    private Class<?> implementorClass;

    public ImplementorTest() {
    }

    public ImplementorTest(Class<?> implementorClass) {
        if (implementorClass == null) {
            throw new IllegalArgumentException("implementorClass");
        }

        this.implementorClass = implementorClass;
    }

    /** Uses to clean output directory after every test. Be careful. */
    private void deleteFolderContent(File folder, boolean isInner) {
        File[] files = folder.listFiles();
        if(files!=null) { //some JVMs return null for empty dirs
            for(File f: files) {
                if(f.isDirectory()) {
                    deleteFolderContent(f, true);
                } else {
                    f.delete();
                }
            }
        }
        if (isInner) {
            folder.delete();
        }
    }

    /** By default, cleaning up is disabled */
    @AfterTest(enabled = false)
    public void cleanUp() {
        deleteFolderContent(new File(OUTPUT_DIRECTORY), false);
    }

    /*
     * TESTS
     */

    public void shouldBeConstructorWithStringParameter() throws Exception {
        newImplementor();
    }

    public void implementCloneable() throws Exception {
        checkInterfaceImplementationFromStandardLibrary("java.lang.Cloneable");
    }

    /*
     * END OF TESTS
     */


    /*
     * CHECKERS METHODS. Use it to compile, load and check result of your program.
     */
    private void checkInterfaceImplementationFromFolder(String className) throws Exception {
        Implementor implementor = newImplementor();
        String implClassName = implementor.implementFromDirectory(TESTS_DIRECTORY, className);
        compileAndCheckInterfaceImplementation(className, implClassName);
    }

    private void checkInterfaceImplementationFromStandardLibrary(String className) throws Exception {
        Implementor implementor = newImplementor();
        String implClassName = implementor.implementFromStandardLibrary(className);
        compileAndCheckInterfaceImplementation(className, implClassName);
    }

    private void checkAbstractClassImplementationFromFolder(String className) throws Exception {
        Implementor implementor = newImplementor();
        String implClassName = implementor.implementFromDirectory(TESTS_DIRECTORY, className);
        compileAndCheckAbstractClassImplementation(className, implClassName);
    }

    private void checkAbstractClassImplementationFromStandardLibrary(String className) throws Exception {
        Implementor implementor = newImplementor();
        String implClassName = implementor.implementFromStandardLibrary(className);
        compileAndCheckAbstractClassImplementation(className, implClassName);
    }

    /*
     * CHECKERS METHODS END
     */

    private void compileAndCheckInterfaceImplementation(String className, String implClassName) throws IOException {
        final Class<?> outputClass = compileAndLoadClass(implClassName);
        checkImplementsInterface(className, outputClass);
    }

    private void compileAndCheckAbstractClassImplementation(String className, String implClassName) throws IOException {
        final Class<?> outputClass = compileAndLoadClass(implClassName);
        checkExtendsAbstractClass(className, outputClass);
    }

    private void checkExtendsAbstractClass(String className, Class<?> outputClass) {
        assertThat(outputClass.getSuperclass().getCanonicalName()).isEqualTo(className);
    }


    private Class<?> compileAndLoadClass(String implClassName) throws IOException {
        final String outputAbsolutePath = getAbsolutePath(implClassName);
        tryToCompile(outputAbsolutePath);
        final Class<?> outputClass = loadClassFromTestDirectory(implClassName);
        checkIsNotAbstract(outputClass);
        return outputClass;
    }


    private void checkImplementsInterface(String className, Class<?> aClass) {
        assertThat(aClass.getInterfaces()).hasSize(1);
        assertThat(aClass.getInterfaces()[0].getCanonicalName()).isEqualTo(className);
    }

    private void checkIsNotAbstract(Class<?> aClass) {
        assertThat(Modifier.isAbstract(aClass.getModifiers())).isFalse();
    }

    private void tryToCompile(String outputAbsolutePath) throws IOException {
        assertThat(compileFile(outputAbsolutePath)).isTrue().as("Can't compile " + outputAbsolutePath);
    }

    private String getAbsolutePath(String implClassName) {
        final String[] split = implClassName.split("\\.");
        split[split.length - 1] += ".java";
        return Paths.get(OUTPUT_DIRECTORY, split).toAbsolutePath().toString();
    }

    private boolean compileFile(String absolutePath) throws IOException {
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        StandardJavaFileManager fileManager = compiler.getStandardFileManager(diagnostics, null, null);
        Iterable<? extends JavaFileObject> compilationUnits = fileManager.getJavaFileObjectsFromStrings(
                Arrays.asList(absolutePath));
        List<String> options = new ArrayList<>();
        options.addAll(Arrays.asList("-classpath", System.getProperty("java.class.path") + TESTS_DIRECTORY));
        JavaCompiler.CompilationTask task = compiler.getTask(null, fileManager, diagnostics, options,
                null, compilationUnits);
        boolean success = task.call();
        if (!success) {
            for (Diagnostic<? extends JavaFileObject> diagnostic : diagnostics.getDiagnostics()) {
                System.err.println(diagnostic.toString());
            }
        }
        fileManager.close();
        return success;
    }

    private Class<?> loadClassFromTestDirectory(String className) {
        File outputDirectoryFile = new File(OUTPUT_DIRECTORY);
        File testDirectoryFile = new File(TESTS_DIRECTORY);

        try {
            URL[] urls = new URL[]{outputDirectoryFile.toURI().toURL(),
                    testDirectoryFile.toURI().toURL()};

            ClassLoader cl = new URLClassLoader(urls);
            return cl.loadClass(className);
        } catch (MalformedURLException | ClassNotFoundException ignored) {
            throw new RuntimeException("Class cannot be loaded");
        }
    }

    /**
     * This is constructor for your Implementor implementation (construct with OUTPUT_DIRECTORY parameter).
     */
    private Implementor newImplementor() throws Exception {
        Constructor<?> constructor = getStringConstructor();
        constructor.setAccessible(true);
        return (Implementor) constructor.newInstance(OUTPUT_DIRECTORY);
    }

    private Constructor<?> getStringConstructor() throws Exception {
        return implementorClass.getDeclaredConstructor(String.class);
    }

}
