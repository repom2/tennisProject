import {useResolvePromise} from "common/hooks/util-hooks";
import {getPlayers} from "data/DataFetch";
import {Players} from "data/openapi";


export const useGetPlayers = () => {
    return useResolvePromise<Players>({
        queryFn: () => getPlayers({'level': 'all'}),
        queryKey: ["PLAYERS"],
        cacheTime: 1,
        onError: (error) => {
            console.log("ERROR HERE", error);
        },
    });
};