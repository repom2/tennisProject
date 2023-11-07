import {isNotNil} from "common/functions/commonFunctions";
import {ApiError} from "data/openapi";
import {useQuery, UseQueryOptions} from "react-query";
import {UseQueryResult} from "react-query/types/react/types";
import {useLocation, useSearchParams} from "react-router-dom";


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
