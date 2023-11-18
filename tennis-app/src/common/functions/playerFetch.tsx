import {useResolvePromise} from "common/hooks/util-hooks";
import {getPlayers} from "data/DataFetch";
import {Players} from "data/openapi";

export const useGetPlayers = () => {
    return useResolvePromise<Players>({
        queryFn: () => {
            return getPlayers({
                level: "all",
            });
        },
        queryKey: ["PLAYERS"],
    });
};
