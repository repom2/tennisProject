import React, { useEffect, useState } from 'react';
import {Players} from 'data/openapi/models/Players';
import {getData} from 'common/functions/playerData';


export const MyComponent: React.FC = () => {
  const [data, setData] = useState<Players | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getData()
    .then((data: Players) => {
      setData(data);
    })
      .catch((error: Error) => {
        setError(error.message);
      });
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  } else if (data) {
    return (
      <div>

          // Render your data here.
          data?.0.last_name

      </div>
    );
  } else {
    return <div>Loading...</div>;
  }
};