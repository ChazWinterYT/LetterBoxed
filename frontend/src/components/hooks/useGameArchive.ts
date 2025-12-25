import { useState, useEffect, useRef } from "react";
import { getGamesFromCache, saveGamesToCache } from "../../utility/gameCache";
import { Game } from "../../types/Game";

interface FetchResult {
  items: Game[];
  lastKey?: any;
}

export const useGameArchive = (
  cacheKey: string,
  fetchFunction: (lastKey: any) => Promise<FetchResult>
) => {
  const [games, setGames] = useState<Game[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  // Use ref to keep track of games without triggering re-renders inside loops
  const gamesRef = useRef<Game[]>([]);

  useEffect(() => {
    let isMounted = true;
    
    const loadAndSync = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // 1. Load from Cache
        const cachedEntry = await getGamesFromCache(cacheKey);
        let currentGames = cachedEntry?.games || [];
        let tailKey = cachedEntry?.lastKey;
        
        // Update state immediately if we have cached games
        if (currentGames.length > 0) {
            setGames(currentGames);
            gamesRef.current = currentGames;
        }

        // 2. Head Sync (Fetch updates)
        // We fetch from the start (lastKey=null) until we find an overlap or run out.
        let headKey = null;
        let newGames: Game[] = [];
        let overlapFound = false;
        
        // Safety limit to prevent infinite loops
        const MAX_PAGES = 50; 
        let pagesFetched = 0;

        while (pagesFetched < MAX_PAGES) {
            // console.log("Syncing head, page:", pagesFetched + 1);
            const data: FetchResult = await fetchFunction(headKey);
            const fetchedItems = data.items;
            
            if (fetchedItems.length === 0) {
                break; // No more games on server
            }

            // Check for overlap
            if (currentGames.length > 0) {
                const firstCachedId = currentGames[0].gameId;
                // Check if the most recent cached game is in this batch
                const matchIndex = fetchedItems.findIndex((g: Game) => g.gameId === firstCachedId);
                
                if (matchIndex !== -1) {
                    // Overlap found!
                    // Take items before the match
                    const newItems = fetchedItems.slice(0, matchIndex);
                    newGames = [...newGames, ...newItems];
                    overlapFound = true;
                    break;
                } else {
                    // No overlap in this batch, take all and continue
                    newGames = [...newGames, ...fetchedItems];
                    headKey = data.lastKey;
                    if (!headKey) break; // End of server list
                }
            } else {
                // Cache is empty, just accumulate
                newGames = [...newGames, ...fetchedItems];
                headKey = data.lastKey;
                
                // Update state incrementally
                if (isMounted) {
                    setGames([...newGames]);
                }

                if (!headKey) {
                    tailKey = null; // We fetched everything
                    break;
                }
            }
            pagesFetched++;
        }

        if (overlapFound || currentGames.length > 0) {
             // Merge: New Games + Existing Cached Games
             currentGames = [...newGames, ...currentGames];
        } else {
            // Cache was empty and we fetched everything or stopped
            currentGames = newGames;
            // If we stopped but have a next key, that becomes our tail key
            if (!tailKey && headKey) {
                tailKey = headKey;
            }
        }
        
        // Update state with merged list
        if (isMounted) {
            setGames(currentGames);
            gamesRef.current = currentGames;
        }
        
        // Save sync point
        await saveGamesToCache(cacheKey, currentGames, tailKey);

        // 3. Tail Sync (Fetch history if incomplete)
        // If we have a tailKey, it means we haven't reached the end of history.
        if (tailKey) {
             // console.log("Syncing tail from:", tailKey);
             while (tailKey && isMounted) {
                 const data: FetchResult = await fetchFunction(tailKey);
                 const fetchedItems = data.items;
                 if (fetchedItems.length === 0) break;
                 
                 currentGames = [...currentGames, ...fetchedItems];
                 tailKey = data.lastKey;
                 
                 if (isMounted) {
                     setGames(currentGames);
                 }
                 
                 // Save progress periodically
                 await saveGamesToCache(cacheKey, currentGames, tailKey);
             }
        }
        
      } catch (err) {
        console.error("Error in useGameArchive:", err);
        if (isMounted) setError(err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadAndSync();

    return () => {
      isMounted = false;
    };
  }, [cacheKey, fetchFunction]);

  return { games, isLoading, error };
};
