module HW3 where
import Data.Complex
import Data.List

--1
newtype Matrix a = Matrix [[a]]

instance Show a => Show (Matrix a) where
    showsPrec _ = myShowMatrix

myShowMatrix :: Show a => Matrix a -> ShowS
myShowMatrix (Matrix (x:[])) = showList x 
myShowMatrix (Matrix (x:xs)) = showList x . showChar '\n' . (myShowMatrix $ Matrix xs)
myShowMatrix _ = showString "EMPTY"

--2
newtype Cmplx = Cmplx (Complex Double) deriving Eq

instance Show Cmplx where
    showsPrec _ = myShowCmplx

myShowCmplx :: Cmplx -> ShowS
myShowCmplx (Cmplx c) = shows (realPart c) 
                        . showString ((if signum (imagPart c) > 0 then '+' else '-'):"i*")
                        . shows (abs (imagPart c))

instance Read Cmplx where
    readsPrec _ = myReadCmplxReal

myReadCmplxReal :: ReadS Cmplx
myReadCmplxReal v = [(Cmplx $ (fst realPart) :+ imagPartSign * imagPart, rest)] where
    realPart :: (Double, String)
    realPart = head ((reads v)::[(Double, String)])
    
    parseImagPartSign :: String -> (Double, String)
    parseImagPartSign (sign:i:m:rest) = (if (sign == '+') then 1.0 else (-1.0), rest)
    
    getImagPart :: String -> (Double, String)
    getImagPart s = head ((reads s)::[(Double, String)])

    p1 :: (Double, String)
    p1@(imagPartSign, imagPartRestStr) = parseImagPartSign $ snd realPart
    p2 :: (Double, String)
    p2@(imagPart, rest) = getImagPart imagPartRestStr

-- 3
comb :: Int -> [a] -> [[a]]
comb 0 _  = [[]]
comb n xs = [y:ys | y:xs' <- tails xs, ys <- comb (n - 1) xs']

-- 4
class (Eq a, Enum a, Bounded a) => SafeEnum a where
    ssucc :: a -> a
    spred :: a -> a

    ssucc x = if x == maxBound then minBound else succ x
    spred x = if x == minBound then maxBound else pred x


-- Examples
m = Matrix [[1,2,3],[4,5,6],[7,8,9]]

cx1 = Cmplx $ (-2.7) :+ (-3.4)
cx2 = Cmplx $ (1e-2) :+ (23.5)
cx1' = (reads (show cx1))::[(Cmplx, String)]
cx2' = (reads (show cx2))::[(Cmplx, String)]

c = take 4 $ comb 3 [1..]

instance SafeEnum Bool
sf = ssucc False
