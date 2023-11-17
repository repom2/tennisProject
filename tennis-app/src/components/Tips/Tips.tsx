import React, { useEffect, useState } from 'react';
import {useGetPlayers} from 'common/functions/playerFetch';
import {getData} from 'common/functions/playerData';
import { useQuery } from 'react-query';
import {EloRatings} from "data/openapi";



export const Tips: React.FC = () => {
    //const {data, isLoading, isError} = useGetPlayers();
    const joo: string = 'joo';

    return (
    <div className="player-list">
    {joo}
    <h1>kkkkkk</h1>
    </div>
  );
};
