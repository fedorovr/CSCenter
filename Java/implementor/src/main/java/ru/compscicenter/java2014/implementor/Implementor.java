package ru.compscicenter.java2014.implementor;

/**
 * Created by Roman Fedorov on 30.11.2014.
 */

public interface Implementor {
    String implementFromDirectory(final String directoryPath,
                          final String className) throws ImplementorException;

    String implementFromStandardLibrary(final String className)
                                                  throws ImplementorException;
}
