import {ApiError} from "data/openapi";
import {useQuery, UseQueryOptions} from "react-query";
import {UseQueryResult} from "react-query/types/react/types";
import {SetRequired} from "type-fest";


/** A typesafe way to ensure that value is null or undefined */
export const isNil = <T>(value: T | null | undefined): value is undefined | null => {
    return value === null || value === undefined;
};

/** A typesafe way to ensure that value is not null or undefined */
export const isNotNil = <T>(value: T | undefined | null): value is NonNullable<T> => {
    return !isNil(value);
};

type ResolvePromiseQueryOptions<TQueryFnData, TData> = Omit<
    SetRequired<
        UseQueryOptions<
            TQueryFnData,
            ApiError,
            TData,
            Array<string | number | Array<string | number | undefined | null> | undefined | null>
        >,
        "queryKey"
    >,
    "placeholderData"
>;

export function useResolvePromise<TQueryFnData, TData = TQueryFnData>(
    options: ResolvePromiseQueryOptions<TQueryFnData, TData>
): UseQueryResult<TData, ApiError> {
    /*
    Filter out undefined and null values from the queryKey to avoid unnecessary re-fetches,
    and then Cast the type "queryKey" wider than it actually is to make the typescript compiler happy */
    const queryKey: Array<
        string | number | Array<string | number | undefined | null> | undefined | null
    > = options.queryKey.filter(isNotNil);
    return useQuery({...options, queryKey});
}