import React, { useEffect, useState } from 'react';
import {useGetPlayers} from 'common/functions/playerFetch';
import {getData} from 'common/functions/playerData';


export const MyComponent: React.FC = () => {
    const {data: elo} = useGetPlayers();
    const play = getData();
    console.log(play);
    return (
      <div>
        <h1>elo</h1>
      </div>
    );
};
