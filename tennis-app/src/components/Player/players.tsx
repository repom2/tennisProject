import React, { useEffect, useState } from 'react';
import {useGetPlayers} from 'common/functions/playerFetch';
import {getData} from 'common/functions/playerData';
import { useQuery } from 'react-query';


export const MyComponent: React.FC = () => {
    //const {data, isLoading, isError} = useGetPlayers();
    const { isLoading, isError, data, error } = useQuery('players', getData);

    if (isLoading)
        return <div></div>;

    if (isError)
        return <div></div>;

    return (
        <div>
            {data && data.data.map(player => ( // don't forget to access response.data
                <div key={player.id}>
                    <p>Name: {player.first_name}</p>
                    <p>Level: {player.last_name}</p>
                    {/* Other player properties */}
                </div>
            ))}
        </div>
    );
};
