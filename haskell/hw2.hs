module HW2 where
import Data.List

-- 1
data LogLevel = Error | Warning | Info deriving Show

cmp :: LogLevel -> LogLevel -> Ordering
cmp Error Error = EQ
cmp Warning Warning = EQ
cmp Info Info = EQ
cmp Error _ = GT
cmp _ Error = LT
cmp Warning _ = GT
cmp _ Warning = LT

-- 2
data Person = Person { firstName :: String, lastName :: String, age :: Int } deriving Show

abbrFirstName :: Person -> Person
abbrFirstName p = Person {firstName = getName (firstName p), lastName = lastName p, age = age p} where
    getName s     | length s < 2  = s
    getName (s:_) | otherwise     = s:['.']

-- 3
data Tree a = Leaf | Node (Tree a) a (Tree a) deriving Show

treeSum :: Tree Integer -> Integer
treeSum Leaf = 0
treeSum (Node l x r) = treeSum l + x + treeSum r

treeHeight :: Tree a -> Int
treeHeight Leaf = 0
treeHeight (Node l x r) = 1 + max (treeHeight l) (treeHeight r)

-- 4
sum3 :: Num a => [a] -> [a] -> [a] -> [a]
sum3 a b c = sum3helper (reverse $ sortBy lengthOrdering [a, b, c]) [] where
    sum3helper [(x:xs), (y:ys), (z:zs)] acc = sum3helper [xs, ys, zs] ((x + y + z):acc)
    sum3helper [(x:xs), (y:ys), []    ] acc = sum3helper [xs, ys, []] ((x + y):acc)
    sum3helper [(x:xs), []    , []    ] acc = sum3helper [xs, [], []] (x:acc)
    sum3helper [[]    , []    , []    ] acc = reverse acc
    lengthOrdering x y = compare (length x) (length y)

-- 5
digits :: Integer -> [Integer]
digits x = digitsHelper (abs x) [] where
    digitsHelper 0 []  = [0]
    digitsHelper 0 acc = acc
    digitsHelper x acc = digitsHelper (x `div` 10) ((x `mod` 10):acc)

-- 6
containsAllDigits :: Integer -> Bool
containsAllDigits n = all (`elem` (digits n)) [1..9] 

-- 7
containsAllDigitsOnes :: Integer -> Bool
containsAllDigitsOnes n = sort (filter (>0) (digits n)) == [1..9]

-- 8
sublist :: Int -> Int -> [a] -> [a]
sublist l r xs = drop l (take r xs) 

-- 9
repeatEveryElem :: Int -> [a] -> [a]
repeatEveryElem n l = [c | c <- l, _ <- [1..n]]

--10
movingLists :: Int -> [a] -> [[a]]
movingLists n l = movingListsHelper 0 where
    movingListsHelper idx = if (length s == n) then s:(movingListsHelper $ idx + 1) else [] where 
        s = sublist idx (idx + n) l


-- Examples
example10_0 = movingLists 2 [5..8]
example10_1 = take 10 $ movingLists 2 [5..]

example8_0 = sublist 2 5 "abcdefgh"
example8_1 = sublist 5 2 "abcdefgh"
example8_2 = sublist 2 9 ['a'..]
