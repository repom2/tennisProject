
import {
    getPlayers
} from "data/DataFetch";
import { useResolvePromise } from "hooks/useResolvePromise";


export const useGetPlayers = (
) => {

    return useResolvePromise({
        queryFn: () =>
            getPlayers(),
        select(response) {
            return response;
        },
        queryKey: ["PLAYERS", ],
    });
};

