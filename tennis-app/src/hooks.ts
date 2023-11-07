import {getPlayers} from "data/DataFetch";
import {useResolvePromise} from "common/hooks/util-hooks";


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

