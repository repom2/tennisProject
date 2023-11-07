/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */

/** Function for creating classNames for components.
 * Accepts any number of strings or falsy values as argument.
 * Examples:
 * createClassName(styles.container, loading && styles.loading)
 * -> 'container loading' (when loading) | 'container' (when not)*/
export const createClassName = (...classNames: Array<string | 0 | null | undefined | false>) => {
    return classNames.filter(Boolean).join(" ");
};

/** A typesafe way to ensure that value is null or undefined */
export const isNil = <T>(value: T | null | undefined): value is undefined | null => {
    return value === null || value === undefined;
};

/** A typesafe way to ensure that value is not null or undefined */
export const isNotNil = <T>(value: T | undefined | null): value is NonNullable<T> => {
    return !isNil(value);
};

