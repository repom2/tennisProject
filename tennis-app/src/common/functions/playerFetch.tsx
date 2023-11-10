import {useResolvePromise} from "common/hooks/util-hooks";
import {getPlayers} from "data/DataFetch";


export const useGetPlayers = () => {
    return useResolvePromise({
        queryFn: () => getPlayers({'level': 'all'}),
        queryKey: ["PLAYERS"],
        cacheTime: 1,
        onError: (error) => {
            console.log("ERROR HERE", error);
        },
    });
};