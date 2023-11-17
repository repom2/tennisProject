import React, { useEffect, useState } from 'react';
import {useGetPlayers} from 'common/functions/playerFetch';
import {getData} from 'common/functions/playerData';
import { useQuery } from 'react-query';
import {EloRatings} from "data/openapi";
import './PlayerList.css';


export const PlayerList: React.FC = () => {
    //const {data, isLoading, isError} = useGetPlayers();
    const { isLoading, isError, data, error } = useQuery('eloratings', getData);

    if (isLoading)
        return <div></div>;

    if (isError)
        return <div></div>;

    return (
    <div className="main">
    <ul className="player-list">
        <li className="player-list-item player-list-item-header">
          <div><strong>Player</strong></div>
          <div><strong>Elo</strong></div>
          <div><strong>Date</strong></div>
        </li>
      {data && data.data && data.data.map((player: EloRatings) => (
        <li key={player.id} className="player-list-item">
          <div>{player.first_name} {player.last_name}</div>
          <div>{player.elo}</div>
          <div>{player.latest_date ? new Date(player.latest_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }): "Not available"}</div>
        </li>
      ))}
    </ul>
    </div>
  );
};
