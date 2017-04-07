import Control.Applicative (ZipList(ZipList), getZipList)
import Data.List

-- 1: use applicative functors to express ZipList
x1s = [1,2,3]
x2s = [4,5,6]
x3s = [7,8,9]
x4s = [10,11,12]

z4 =  zipWith4 (\a b c d -> 2*a+3*b+5*c-4*d) x1s x2s x3s x4s

z4ap = getZipList $ (\a b c d -> 2*a+3*b+5*c-4*d) <$> ZipList x1s <*> ZipList x2s <*>ZipList x3s <*> ZipList x4s

-- Implement operators to hide some ZipList (un)packing noise
(>*<) :: [] (a -> b) -> [] a -> [] b
(>*<) gs xs = getZipList $ (ZipList gs) <*> (ZipList xs)

(>$<) :: (a -> b) -> [] a -> [] b
(>$<) f xs = getZipList $ fmap f (ZipList xs)

z4ap' = (\a b c d -> 2*a+3*b+5*c-4*d) >$< x1s >*< x2s >*< x3s >*< x4s

-- 2: Implement Functor and Applicative for 3d vector
data Triple a = Tr a a a deriving (Eq,Show)

instance Functor Triple where
    fmap f (Tr x y z) = Tr (f x) (f y) (f z)

instance Applicative Triple where
    pure x = Tr x x x
    (Tr f1 f2 f3) <*> (Tr x y z) = Tr (f1 x) (f2 y) (f3 z)

triple = (^2) <$> Tr 1 (-2) 3
triple' =  Tr (^2) (+2) (*3) <*> Tr 2 3 4

-- 3: Implement Functor and Applicative for Tree
data Tree a = Nil | Branch (Tree a) a (Tree a) deriving (Eq, Show)

instance Functor Tree where
    fmap f Nil = Nil
    fmap f (Branch left x right) = Branch (fmap f left) (f x) (fmap f right)

instance Applicative Tree where
    pure x = Branch (pure x) x (pure x)
    Nil <*> x = Nil
    f <*> Nil = Nil
    (Branch fl f fr) <*> (Branch l x r) = Branch (fl <*> l) (f x) (fr <*> r)

tree1 = Branch (Branch Nil 7 Nil) 2 Nil
tree2 = Branch (Branch Nil 3 Nil) 4 (Branch Nil 5 Nil)
tree' = (*) <$> tree1 <*> tree2
tree'' = Branch (Branch Nil (+3) Nil) (*2) Nil <*> Branch Nil 7 (Branch Nil 5 Nil)

-- 4: Implement Functor and Applicative for composition
newtype Cmps f g x = Cmps {getCmps :: f (g x)} deriving (Eq, Show) 

instance (Functor f, Functor g) => Functor (Cmps f g) where
    fmap foo (Cmps c) = Cmps (fmap (fmap foo) c)

instance (Applicative f, Applicative g) => Applicative (Cmps f g) where
    pure x = Cmps (pure (pure x))
    Cmps f <*> Cmps x = Cmps ((fmap (<*>) f) <*> x)

cmps' = getCmps $ (+) <$> Cmps [Just 1, Just 2] <*> Cmps [Nothing, Just 40]

-- 5: Fold list with division and save log
divideList' :: (Show a, Fractional a) => [a] -> (String,a)
divideList' xs = (\ (log, res) -> (tail log, res)) (divideListHelper xs) where
    divideListHelper []     = ("/" ++ show 1.0, 1.0)
    divideListHelper (x:xs) = (/) <$> ("/<-" ++ show x, x) <*> (divideListHelper xs)

divideListExample = divideList' [3,4,5]

-- 6: Implement Functor and Applicative for composition (I don't shure is it correct or not)
newtype Arr2 e1 e2 a = Arr2 { getArr2 :: e1 -> e2 -> a }

instance Functor (Arr2 t p) where
    fmap f (Arr2 g) = Arr2 (\ x y -> f (g x y))  

instance (Monoid t, Monoid p) => Applicative (Arr2 t p) where
    pure v = Arr2 (\x y -> v)
    Arr2 f <*> g = fmap (f mempty mempty) g
