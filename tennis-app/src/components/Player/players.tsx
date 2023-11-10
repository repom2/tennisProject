import React, { useEffect, useState } from 'react';
import {Players} from 'data/openapi/models/Players';
//import {getData} from 'common/functions/playerData';
import {useGetPlayers} from 'common/functions/playerFetch';


export const MyComponent: React.FC = () => {
    const {data: elo} = useGetPlayers();
    //console.log(elo);
    return (
      <div>
          data?.0.last_name
      </div>
    );
};
