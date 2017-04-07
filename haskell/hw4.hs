module HW4 where
import Data.Monoid
import Data.List
import Data.Char

-- Endomorphism
newtype Endom a = Endom { appEndom :: a -> a }

instance Monoid (Endom a) where
    mempty = Endom id
    Endom f `mappend` Endom g = Endom (f . g)

fn = mconcat $ map Endom [(+5), (*3), (^2)]
r = appEndom fn 2

Dual fn' = mconcat $ map (Dual . Endom) [(+5),(*3),(^2)]
r' = appEndom fn' 2

-- Express library functions with fold*
or' :: [Bool] -> Bool
or' = foldr (||) False

length' :: [a] -> Int
length' = foldr (\x acc -> acc + 1) 0

maximum' :: Ord a => [a] -> a
maximum' = foldr1 (\x acc -> max x acc) 

head' :: [a] -> a
head' = foldl1 (\x acc -> x)

last' :: [a] -> a
last' = foldr1 (\acc x -> x)

filter' :: (a -> Bool) -> [a] -> [a]
filter' p = foldr (\x acc -> if p x then (x:acc) else acc) []

map' :: (a -> b) -> [a] -> [b]
map' f = foldr (\x acc -> (f x):acc) []

-- Some more examples of using folds
charRange :: (Char,Char) -> [Char]
charRange (start, end) = unfoldr (\c -> if c > end then Nothing else Just (c, nextChar c)) start where
    nextChar c = chr (ord c + 1)

revRange :: (Char,Char) -> [Char]
revRange (end, start) = unfoldr (\c -> if c >= end then Just (c, prevChar c) else Nothing) start where
    prevChar c = chr (ord c - 1)

revRange' :: (Char,Char) -> [Char]
revRange' = unfoldr fun where
    fun :: (Char, Char) -> Maybe (Char, (Char, Char))
    fun (end, curChar) = (\c -> if c >= end then Just (c, (end, prevChar c)) else Nothing) curChar 
    prevChar c = chr (ord c - 1)

--
inits' :: [a] -> [[a]]
inits' = foldr fun ini where
    fun = (\x acc -> []:(map (\subAcc -> x:subAcc) acc))
    ini = [[]]

tails' :: [a] -> [[a]]
tails' = foldr fun ini where
    fun = (\x acc -> (x:(head acc)):acc)
    ini = [[]]

--
reverse' :: [a] -> [a]
reverse' = foldr fun ini where
    fun = (\x acc -> acc ++ [x])
    ini = []

reverse'' :: [a] -> [a]
reverse'' = foldl fun ini where
    fun = (\acc x -> x:acc)
    ini = []

-- "Additional parameter" technique
-- Example:
take' :: Int -> [a] -> [a]
take' n xs = foldr step ini xs n where
    step :: a -> (Int -> [a]) -> Int -> [a]
    step x g 0 = []
    step x g n = x : (g (n - 1))
    ini :: Int -> [a]
    ini = const []

-- Task: implement safe list indexing
infixl 9 !!!

(!!!) :: [a] -> Int -> Maybe a
xs !!! n = foldr fun ini xs n where
    fun :: a -> (Int -> Maybe a) -> Int -> Maybe a
    fun x g n | n < 0  = Nothing
    fun x g n | n == 0 = Just x
    fun x g n | n > 0  = g (n - 1)
    ini :: Int -> Maybe a
    ini = const Nothing

-- implement foldl with foldr 
foldl'' :: (b -> a -> b) -> b -> [a] -> b
foldl'' f v xs = foldr (fun f) ini xs v where
    fun :: (b -> a -> b) -> a -> (b -> b) -> b -> b
    fun f x g n = g $ f n x 
    ini :: b -> b
    ini = id

-- Foldable with different tree traversals
data Tree a = Nil | Branch (Tree a) a (Tree a) deriving (Eq, Show)
newtype Preorder a   = PreO   (Tree a) deriving (Eq, Show)
newtype Postorder a  = PostO  (Tree a) deriving (Eq, Show)
newtype Levelorder a = LevelO (Tree a) deriving (Eq, Show)

-- inorder
instance Foldable Tree where
    foldr f ini tree = foldr f ini (inorder tree) where
        inorder :: Tree a -> [a]
        inorder Nil = []
        inorder (Branch l x r) = inorder l ++ [x] ++ inorder r

instance Foldable Preorder where
    foldr f ini (PreO tree) = foldr f ini (preorder tree) where
        preorder Nil = []
        preorder (Branch l x r) = [x] ++ preorder l ++ preorder r

instance Foldable Postorder where
    foldr f ini (PostO tree) = foldr f ini (postorder tree) where
        postorder Nil = []
        postorder (Branch l x r) = postorder l ++ postorder r ++ [x]

instance Foldable Levelorder where
    foldr f ini (LevelO tree) = foldr f ini (levelOrder tree) where
        levelOrder :: Tree a -> [a]
        levelOrder tree = levelHelper [tree] [] where
            levelHelper :: [Tree a] -> [Tree a] -> [a]
            levelHelper (Nil:xs) nextLevel = levelHelper xs nextLevel
            levelHelper ((Branch l x r):xs) nextLevel = x:(levelHelper xs (nextLevel ++ [l, r]))
            levelHelper [] [] = []
            levelHelper [] nextLevel = levelHelper nextLevel []
