import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/hooks/use-toast';
import { Brain, Users, Bot, ArrowLeft, Zap } from 'lucide-react';

const Matchmaking = () => {
  const [isSearching, setIsSearching] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [matchFound, setMatchFound] = useState(false);
  const [opponent, setOpponent] = useState<{ name: string; elo: number; isAI: boolean } | null>(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isSearching && !matchFound) {
      interval = setInterval(() => {
        setSearchTime(prev => {
          // Simulate finding an opponent or AI fallback after 30 seconds
          if (prev >= 30) {
          const isAIFallback = Math.random() > 0.3; // 70% chance of AI fallback
          
          if (isAIFallback) {
            setOpponent({
              name: 'AI Challenger',
              elo: (user?.elo || 1200) + Math.floor(Math.random() * 200) - 100,
              isAI: true
            });
          } else {
            setOpponent({
              name: `Player_${Math.floor(Math.random() * 9999)}`,
              elo: (user?.elo || 1200) + Math.floor(Math.random() * 200) - 100,
              isAI: false
            });
          }
          
          setMatchFound(true);
          setIsSearching(false);
          
          toast({
            title: "Match found!",
            description: isAIFallback ? "AI opponent ready for battle" : "Human opponent found",
          });
          }
          return prev + 1;
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isSearching, matchFound, user?.elo]);

  const startSearch = () => {
    setIsSearching(true);
    setSearchTime(0);
    setMatchFound(false);
    setOpponent(null);
  };

  const cancelSearch = () => {
    setIsSearching(false);
    setSearchTime(0);
    setMatchFound(false);
    setOpponent(null);
  };

  const startDebate = () => {
    // In a real app, this would pass the opponent data to the debate page
    navigate('/debate', { 
      state: { 
        opponent,
        topic: getRandomTopic()
      } 
    });
  };

  const getRandomTopic = () => {
    const topics = [
      "Artificial Intelligence will make human intelligence obsolete",
      "Social media does more harm than good for society",
      "Privacy is more important than security in the digital age",
      "Remote work is better than office work",
      "Video games have a positive impact on cognitive development",
      "Universal Basic Income should be implemented globally",
      "Space exploration is a waste of resources",
      "Genetic engineering should be allowed for enhancement",
      "Cryptocurrency will replace traditional currency",
      "Climate change requires immediate drastic action"
    ];
    return topics[Math.floor(Math.random() * topics.length)];
  };

  return (
    <div className="min-h-screen bg-gradient-bg">
      <header className="border-b border-border/50 bg-card/20 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-cyber-red" />
            <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              MindGrid
            </h1>
          </div>
          <div className="w-24" /> {/* Spacer for center alignment */}
        </div>
      </header>

      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          {!isSearching && !matchFound && (
            <Card className="bg-gradient-card border-border/50 p-8 text-center">
              <div className="mb-8">
                <Users className="h-16 w-16 text-cyber-blue mx-auto mb-4" />
                <h2 className="text-3xl font-bold text-foreground mb-2">
                  Enter the Neural Arena
                </h2>
                <p className="text-muted-foreground mb-6">
                  We'll match you with an opponent based on your skill level
                </p>
                <div className="flex items-center justify-center space-x-6 text-sm text-muted-foreground mb-8">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-cyber-green rounded-full"></div>
                    <span>ELO Matching</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-cyber-blue rounded-full"></div>
                    <span>Real-time Debate</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-cyber-gold rounded-full"></div>
                    <span>AI Fallback</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <div className="bg-muted/20 rounded-lg p-4">
                  <p className="text-sm text-muted-foreground">Your ELO</p>
                  <p className="text-2xl font-bold text-cyber-red">{user?.elo}</p>
                </div>
                <div className="bg-muted/20 rounded-lg p-4">
                  <p className="text-sm text-muted-foreground">Mind Tokens</p>
                  <p className="text-2xl font-bold text-cyber-gold">{user?.mind_tokens}</p>
                </div>
              </div>

              <Button size="xl" onClick={startSearch}>
                <Zap className="mr-2 h-5 w-5" />
                Find Opponent
              </Button>
            </Card>
          )}

          {isSearching && (
            <Card className="bg-gradient-card border-border/50 p-8 text-center">
              <div className="mb-8">
                <div className="relative mx-auto w-24 h-24 mb-6">
                  <div className="absolute inset-0 border-4 border-cyber-red/30 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-cyber-red border-t-transparent rounded-full animate-spin"></div>
                  <Brain className="absolute inset-0 m-auto h-10 w-10 text-cyber-red" />
                </div>
                
                <h2 className="text-3xl font-bold text-foreground mb-2">
                  Scanning Neural Networks
                </h2>
                <p className="text-muted-foreground mb-4">
                  Searching for worthy opponents...
                </p>
                <p className="text-cyber-blue font-mono text-lg">
                  {searchTime}s
                </p>
              </div>

              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-cyber-red rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-cyber-blue rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-cyber-gold rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <p className="text-sm text-muted-foreground">
                  {searchTime < 15 ? 'Looking for human opponents...' : 
                   searchTime < 30 ? 'Expanding search parameters...' : 
                   'Preparing AI challenger...'}
                </p>
              </div>

              <Button variant="outline" onClick={cancelSearch}>
                Cancel Search
              </Button>
            </Card>
          )}

          {matchFound && opponent && (
            <Card className="bg-gradient-card border-border/50 p-8 text-center">
              <div className="mb-8">
                <div className="w-24 h-24 mx-auto mb-6 bg-gradient-secondary rounded-full flex items-center justify-center">
                  {opponent.isAI ? (
                    <Bot className="h-12 w-12 text-white" />
                  ) : (
                    <Users className="h-12 w-12 text-white" />
                  )}
                </div>
                
                <h2 className="text-3xl font-bold text-foreground mb-2">
                  Match Found!
                </h2>
                <p className="text-muted-foreground mb-6">
                  Opponent ready for neural combat
                </p>
              </div>

              <div className="bg-muted/20 rounded-lg p-6 mb-8">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">You</p>
                    <p className="text-xl font-bold text-foreground">{user?.username}</p>
                    <p className="text-cyber-blue">{user?.elo} ELO</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-4xl mb-2">⚔️</div>
                    <p className="text-sm text-muted-foreground">VS</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">
                      {opponent.isAI ? 'AI Opponent' : 'Player'}
                    </p>
                    <p className="text-xl font-bold text-foreground">{opponent.name}</p>
                    <p className={opponent.isAI ? 'text-cyber-gold' : 'text-cyber-blue'}>
                      {opponent.elo} ELO
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <Button variant="outline" onClick={cancelSearch} className="flex-1">
                  Decline
                </Button>
                <Button onClick={startDebate} className="flex-1" size="lg">
                  <Zap className="mr-2 h-5 w-5" />
                  Start Battle
                </Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Matchmaking;