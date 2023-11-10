


/** Function for creating classNames for components.
 * Accepts any number of strings or falsy values as argument.
 * Examples:
 * createClassName(styles.container, loading && styles.loading)
 * -> 'container loading' (when loading) | 'container' (when not)*/
export const createClassName = (...classNames: Array<string | 0 | null | undefined | false>) => {
    return classNames.filter(Boolean).join(" ");
};