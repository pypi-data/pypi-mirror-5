module luminosity
 contains

subroutine lumfunc(ngalaxies,Np,z,loglum,magr,lumdist,kcorr,absmag,phi,centerabsmag)
 implicit none
! integer, intent(in) :: numlines
 integer :: i, j, k, l, m, n, q, intmin, intmax 
 integer, intent(in) :: ngalaxies
 integer:: intindex
 integer:: numbins, count, cumcount, badbin, count1, count2, count3
 integer, intent(in) :: Np ! Number of magnitude bins for phi(M)
 integer:: minacceptable ! Minimum acceptable # of galaxies per luminosity function's abs. mag. bins.
 
! integer, intent(in) :: Mp ! Number of bins for the selection function S(z)

 logical:: emptybin  ! used to identify whether any abs. mag. bins are empty
 logical:: stilllooking  ! used to indicate whether or not code has found a suitable range of 
                         ! abs. mag. values.
 
 

! Program uses redshift and absolute magnitude data
! to obtain the luminosity function as a function of
! absolute magnitude
! See "Application of the Information Criterion to the 
! Estimation of Galaxy Luminosity Function"
! by Tsutomu T. Takeuchi

! The input values are read from the 9th release of the SDSS data

! The following are 1-D arrays that store the redshift, right ascension, 
! declination, etc. data for each galaxy.  (Could have used a multi-dim
! single array, but felt this made it easier to avoid getting columns of the 
! array "mixed up" in later calculations.
 real(8), intent(in) :: z(ngalaxies)
 real(8), intent(in) :: loglum(ngalaxies)
 real(8), intent(in) :: magr(ngalaxies)
 real(8), intent(in) :: lumdist(ngalaxies)
 real(8), intent(in) :: kcorr(ngalaxies)
 real(8), intent(in) :: absmag(ngalaxies)
 real(8)  :: absmagmax(ngalaxies), absmagmin(ngalaxies) 
 real(8), intent(out) :: centerabsmag(ngalaxies)  ! Stores center values of each of the Np abs. mag. bins
 real(8),allocatable  :: tempphi(:)    ! Stores temp. values of lum. fct value for each bin
 real(8),allocatable  :: temparray(:)  ! temporarily stores values when calculating sum and std dev. 
 real(8), intent(out) :: phi(Np,25)      ! stores iterated values of the luminosity function 
 real(8), dimension(:,:), allocatable :: Hmatrix      ! stores values of the function H for various values of i and j
 real(8), dimension(:,:), allocatable :: Wmatrix      ! stores values of the function W for various values of k and i
 real(8), dimension(:,:), allocatable :: PhiError   ! Array contains error estimates for each value of phi(k)
 real(8), dimension(:,:), allocatable :: sum1, sum2   ! Used to calculate error estimates for the phi(k)
 real(8), dimension(:,:), allocatable :: KronDelta   ! Kronecker Delta
 integer(4), dimension(:,:),allocatable :: ParameterTest ! 2D array used to test for optimal range of abs. mag. values.
 real(8), dimension(:), allocatable :: absmagbin   ! used to count # of galaxies per absm mag. bin when determining limits for lum. fct.
 real(8), dimension(:), allocatable :: Numerator, Denominator ! Arrays contain elements inside sums of 
 real(8), dimension(:), allocatable :: DenomofDenom, NumofDenom      ! Takeuchi's Eqn. 44
 real(8), dimension(:), allocatable :: SelectFunct  ! the selection function S(z)

 real(8) :: H, W, sum, subsum, Quotient
 real(8) :: tempmin, tempmax

 real(8) :: top, bottom, norm ! top and bottom used to calculate S(z), norm is the normalization constant for the selection function S(z)

 real(8) :: maxmagr, minmagr  ! Largest and smallest apparent r-band magnitudes
 real(8) :: Mmax, Mmin  ! Largest and smallest absolute magnitudes
 real(8) :: Mmax2, Mmin2 ! 2nd largest and smallest absolute magnitudes
 real(8) :: Mmax3, Mmin3 ! 3rd largest and smallest absolute magnitudes
 real(8) :: Mmax4, Mmin4 ! 4th largest and smallest absolute magnitudes
 real(8) :: Mmax5, Mmin5 ! 5th largest and smallest absolute magnitudes
 real(8) :: Mlower, Mupper ! abs. mag limits of the survey
 real(8) :: binsize, lsmagbin, rsmagbin, startvalue, temp
 real(8) :: lsabsmagbin, rsabsmagbin ! left and right values of abs. mag bins
 real(8) :: deltaM 
 real(8) :: deltaz
 real(8) :: warningflagH, warningflagW ! warning flag to alert user to potential problems
 real(8) :: randomreal ! random number (for obtaining curve for dimmest possible galaxy to be seen as a function
                    ! of redshift
 
 real(8) :: redshift  ! a particular redshift value within the selection function S(z)
 real(8) :: upperlim, lowerlim   ! upper and lower limits of integral in Steven Murray's Eqn. 2.9
 real(8) :: Mmaxz     ! abs. magnitude of dimmest galaxy that can be seen in survey for a given value of z
 real(8) :: upperz, lowerz ! upper and lower bins limits for z when finding selection function S(z)

 
 real(8), parameter :: sollum = 3.839d26  ! Luminosity of sun (in watts) 
 real(8), parameter :: solabsmag = 4.67d0  ! Need to double check this value; not sure what band this is for. 

! print *, " "
! print *, "Data from 9th release of SDSS"
! print *, "The values being loaded were calculated under the"
! print *, "assumption of a flat cosmology."
! print *, "i.e., the default cosmology in Cosmolopy."
! print *, "Data are from the main ellipse"
! print *, "part of SDSS survey."
! print *, "0.005 <= z <= 0.28"
! print *, "Broadline AGN excluded."
! print *, "Code assumes that data have already been checked for" 
! print *, "duplicate values."
! print *, " "
! print *, "How many lines of data do you wish to use?"
! print *, "(566,687 is the whole file)"
! read(*,*) numlines
! print *, " "
! print *, "What is the minimum acceptable number of galaxies per"
! print *, "abs. mag. bin when calculating the luminosity function?"
! print *, "(recommend no fewer than 3-5)."
! read(*,*) minacceptable
! print *, " "
! print *, "When calculating the luminosity function,"
! print *, " what is the preferred number of bins?"
! print *, "(recommend at least 15)."
! read(*,*) Np
! print *, " "
! print *, "When calculating S(z), what is the preferred number of bins?"
! read(*,*) Mp
! print *, " "

! allocate(z(numlines))
! allocate(ra(numlines))
! allocate(dec(numlines))
! allocate(loglum(numlines))
! allocate(lumdist(numlines))
! allocate(magr(numlines))
! allocate(kcorr(numlines))
! allocate(absmag(numlines))
 
   
! Had trouble reading all these elements from a single data file.  Kind of crude to have separate files
! for all the data elements, I know, but I didn't want to spend a bunch of time working on this detail.
! Also, some of these files may no longer be necessary since I am now getting the luminosity function
! in terms of abs. mag. rather than luminosity.

! open(10, file='SDSSDR9_Ell_z.prn')
! do i = 1, numlines
!      read(10,*) z(i)  
! enddo
! close(10)
! 
! open(20, file='SDSSDR9_Ell_ra.prn')
! do i = 1, numlines
!      read(20,*) ra(i)  
! enddo
! close(20)
!
! open(30, file='SDSSDR9_Ell_dec.prn')
! do i = 1, numlines
!      read(30,*) dec(i)  
! enddo
! close(30)
!
! open(40, file='SDSSDR9_Ell_loglum.prn')
! do i = 1, numlines
!      read(40,*) loglum(i)  
! enddo
! close(40)
!
! open(50, file='SDSSDR9_Ell_magr.prn')
! do i = 1, numlines
!      read(50,*) magr(i)  
! enddo
! close(50)
! 
! open(60, file='SDSSDR9_Ell_lumdist.prn')
! do i = 1, numlines
!      read(60,*) lumdist(i)  
! enddo
! close(60)
!
! open(70, file='SDSSDR9_Ell_kcorr.prn')
! do i = 1, numlines
!      read(70,*) kcorr(i)  
! enddo
! close(70)
!
! open(80, file='SDSSDR9_Ell_absmag.prn')
! do i = 1, numlines
!      read(80,*) absmag(i)  
! enddo
! close(80)

! ngalaxies = numlines

! Code now determines the largest (dimmest) absolute mag.
! and smallest (brightest) absolute mag.
! values of magr
 Mmax = MAXVAL(absmag, ngalaxies)
 Mmin = MINVAL(absmag, ngalaxies) 
 print *,"Largest value of abs. mag is", Mmax
 print *,"Smallest value of abs. mag is", Mmin
 print *, " " 


! Code now determines the largest (dimmest) apparent mag.
! and smallest (brightest) apparent mag.
! values of magr
! tempmin = 1000.0d0
! tempmax = -1000.0d0
! i = 1
! do i = 1, ngalaxies
!      if (magr(i) > tempmax) then
!           tempmax = magr(i)
!           intmax = i
!      endif
!      if (magr(i) < tempmin) then
!           tempmin = magr(i)
!           intmin = i
!      endif
! end do
 maxmagr = maxval(magr)
 minmagr = minval(magr)
 print *,"Row # and largest value of magr is", maxloc(magr), maxmagr
 print *,"Row # and smallest value of magr is", minloc(magr), minmagr
 print *, " " 

! Code now finds the values of absmagmax(z) and absmagmin(z) for each galaxy
! allocate (absmagmax(ngalaxies))  ! dimmest abs. mag. which can be seen at a given redshift
! allocate (absmagmin(ngalaxies))  ! don't need this to get lum fct, but will eventually need this for selection function S(z)
 do i = 1, ngalaxies
      absmagmax(i) = (maxmagr -5.0d0*dlog10(lumdist(i))-25.0d0- &
 & kcorr(i))
      absmagmin(i) = (minmagr -5.0d0*dlog10(lumdist(i))-25.0d0- &
 & kcorr(i))
 end do

 write(*,*) "absmagmax MAX, MIN", maxval(absmagmax), minval(absmagmax) 

 write(*,*) "absmagmin MAX, MIN", maxval(absmagmin), minval(absmagmin)
!****************************************************************************
! Code now determines the optimal range of values for Mlower and Mupper.
! Procedure:
! 1. Start with Mlower = -25 and Mupper = -10 (very few galaxies will have abs. mags. outside this range).  Of course, these limits
!    can be expanded, if need be.
! 2. Count # of galaxies per bin for Np bins; check to see that every bin has at least 'minacceptable' # of galaxies.  
! 3. If so, record Mlower and Mupper and number of galaxies excluded.
! 4. Do so for all possible values of Mlower between -25 and -23 (increment Mlower by +0.5 each time).  Of course,
!    if desired, can make this decrement even smaller (i.e., 0.25, 0.10, etc.).

! 5. Repeat steps 1-4, but now decrementing Mupper by -0.5 each time (Mupper varies between -10 and -12).
! 6. Of the acceptable options, pick the one that excludes the smallest number
!    of galaxies.


 allocate(ParameterTest(25,3))
 ! 25 rows and 3 columns
 ! numbers in first column of array will be trial values of l
 ! numbers in 2nd column will be trial values of m (l and m used to specify Mlower and Mupper)
  
 ! Note:  reason for storing values of l and m, rather than values of
 ! Mlower and Mupper, was an attempt to ensure that calculated bin boundaries for this section are EXACTLY the same as the 
 ! bin boundaries when the luminosity function is actually calculated.  However, even when these bin boundaries are calculated in
 ! exactly the same fashion, and with double precision, there is sometimes (rarely) a slight discrepancy (~2-3 galaxies) between
 ! the two calculations.  For instance, when Mlower = -24 and Mupper = -11, this part of the code determines that 566,665 galaxies
 ! is the optimal number included in the calculation of the luminosity function.  However, the later part of the code (that 
 ! actually calculates the luminosity function) will count 566,663 such galaxies.  This is because of VERY slight differences
 ! in the bin boundaries between the 2 calculations; the bin with boundaries -17.5 and -16.81579 will count 17,904 galaxies in the 
 ! first case, while 17,902 galaxies are counted in the second case.  Not sure what to do about this, unless it is possible to do 
 ! triple precision!  Not really a big deal, however.

 ! numbers in 3rd column will be # of galaxies excluded from trial abs. mag. range.
 ! The number of rows is 25 because, if we allow Mlower to vary from -25 to -23,
 ! and allow Mupper to vary from -10 to -12 (both in 0.5 increment steps), we have 
 ! a total of 25 different possibilites.
 
minacceptable = -1
 ! This section increments Mlower and Mupper
 n = 1   ! n is the current row number in the ParameterTest array.  Acceptable values of l, m, and excluded galaxies are stored here.
 do l = 1, 5
      do m = 1, 5
         Mlower = -25.0d0 + (l-1)*0.5d0
         Mupper = -10.0d0 - (m-1)*0.5d0
         print *, " "
         deltaM = (Mupper - Mlower)/(Np-1) ! Divide by (Np-1) instead of Np to match technique used later in code
!         print *, Mlower, Mupper, Np, deltaM
         emptybin =.false.   ! Assumes that none of the Np trial bins will be empty until proven otherwise.
         cumcount = 0  ! cumcount is number of empty bins; assumes that none are empty at first.
         j = 1
         do while ((emptybin .eqv. .false.) .AND. (j <= Np)) 
            count = 0          ! count is the number of galaxies in each bin.
            lsabsmagbin = Mlower + (j-1)*deltaM - deltaM/2.0d0  ! specifies left side bin boundary
            rsabsmagbin = lsabsmagbin + deltaM                  ! specifies right side bin boundary
            do i = 1,  ngalaxies
               if ((absmag(i) >= lsabsmagbin) .AND. &
 &(absmag(i) < rsabsmagbin)) then
                  count = count + 1
               endif
            end do
            cumcount = cumcount + count
            if (count < minacceptable) then
               emptybin=.true.
            endif
!            print *, j, lsabsmagbin, (rsabsmagbin+lsabsmagbin)/2.0d0&
! &,rsabsmagbin, count, cumcount
            j = j + 1
          end do
          if (emptybin .eqv. .false.) then               ! if requirements satisfied, info stored in ParameterTest array
            print *, Mlower, Mupper, cumcount, &
 &(ngalaxies - cumcount)
            ParameterTest(n,1) = l                  ! stores optimal value of l in memory
            ParameterTest(n,2) = m                  ! stores optimal value of m in memory
            ParameterTest(n,3) = (ngalaxies - cumcount)  ! stores excluded # of galaxies in memory (assumes # is less than 10,000)
!            print *, ParameterTest(n,1), ParameterTest(n,2), &
! &ParameterTest(n,3)
            n = n + 1
          endif
!          print *, " "
      end do
 end do
 
write(*,*) "ParameterTest"
do i=1,25
    write(*,*) ParameterTest(i,:)
end do

 ! Out of the possible acceptable combinations (all Np bins have at least minacceptable galaxies)
 ! picks the one that has the smallest number of excluded galaxies.
 if ((n -1) < 1) then
      print *, "Not possible to meet your specified requirements!!!"
 else
      tempmin = 1.0d23
      l = 1000
      m = 1000
      do q = 1, (n-1)
         if (ParameterTest(q,3) == tempmin) then  ! can handle a "tie" (same # of excluded galaxies) between 2 different abs. mag. ranges.
                                                  ! In case of tie, picks option with the largest possible mag. range.
            if ((l+m) > (ParameterTest(q,1)+ParameterTest(q,2)))&  ! mag. range greatest when sum of l & m smallest.
 & then
                 tempmin = ParameterTest(q,3)
                 l = ParameterTest(q,1)
                 m = ParameterTest(q,2)
            endif
                 
         else if (ParameterTest(q,3) < tempmin) then
               tempmin = ParameterTest(q,3)
               l = (ParameterTest(q,1)) 
               m = (ParameterTest(q,2))
         endif
      end do
      print *, "For", Np, "bins and "
      print *, "a minimum of", minacceptable, "galaxies/bin"
      print *, "the optimal values of Mlower and Mupper are"
      print *, "Mlower = ", -25.0d0 + (l-1)*0.5d0
      print *, "Mupper = ", -10.0d0 - (m-1)*0.5d0
      print *, "# of included galaxies is", int(ngalaxies - tempmin)
      print *, "# of excluded galaxies is", int(tempmin)
      print *, " "
 endif
 
 !*******************************************************************************     
      
 ! Code now begins to calculate the luminosity function
 ! using the information determined above; i.e., the optimal values of Mlower and Mupper

! Code now assigns the initial trial values of
! the luminosity function phi for each magnitude bin
! The number of magnitude bins is Np
! The initial trial luminosity function will be obtained by counting 
! the number of galaxies in each of the Np magnitude bins

! allocate(phi(Np,25))  ! assuming we will not need more than 25 iterations to 
! converge on solution; 5 iterations should be sufficient.
! allocate(centerabsmag(Np))


! Code now assigns initial values to the 2-D Np*20 array phi
! (first iteration)
! centerabsmag(j) is the midpoint of the jth abs. mag. bin
! The first index indicates the number of the jth abs. mag. bin
! and the second index indicates the kth iteration.


! Counts the galaxies within each abs. mag. bin and uses the counts
! to obtain an initial guess for phi for each bin
 if ((n-1) >= 1) then
      Mupper = -10.0d0 - (m-1)*0.5d0
      Mlower = -25.0d0 + (l-1)*0.5d0
      deltaM = (Mupper-Mlower)/(Np-1) ! uses previously determined values of Mlower and Mupper 
      print *, " "
      print *, "DeltaM is ", deltaM
      lsabsmagbin = (Mlower-deltaM/2.0d0) ! starting value of absolute magnitude (lowest luminosity)
      badbin = 0
      cumcount = 0
      print *, " "
      print *, "Counting the galaxies in each abs. mag. bin . . ."
      print *, "        Bin #      LS of Bin            Center of Bin              RS of Bin      &
 &          Galaxies in Bin  Cumm. # of Galaxies"

      do j = 1, Np
         count = 0
         rsabsmagbin = (lsabsmagbin + deltaM)
         i = 1
         do i = 1, ngalaxies
            if ((absmag(i) >= lsabsmagbin) .AND. (absmag(i) < &
 & rsabsmagbin)) then
              count = count + 1
           endif
        end do
        cumcount = cumcount + count
! Since dN = phi*dM, phi = count/(luminosity range) for 1st guess at phi.
        phi(j,1) = count/deltaM
        centerabsmag(j) = lsabsmagbin + deltaM/2.0d0
        if (mod(j, 1) == 0) then
           print *, j, lsabsmagbin, centerabsmag(j), &
 & rsabsmagbin, count, cumcount
        endif
        if (count < minacceptable) then
           badbin = badbin + 1
        endif
        lsabsmagbin = rsabsmagbin
        rsabsmagbin = lsabsmagbin -deltaM
      end do
      if (badbin > minacceptable) then
      print *, "Some bins had less than", minacceptable,"galaxies!"
      endif
 endif

! Non-essential part of code; used as a debugging 'check'.
! print *, " "     
! print *, " "
! 90   format(i4, 1x, f7.3, 1x, e11.4, 1x, e11.4)
! print *, "Here are the intial abs. mag. midpoint and phi values."
! print *, "Phi not yet normalized"
! print *, "but will have units of galaxies per h^3 (Mpc)-3."
! print *, " "
! print *, "j centerabsmag  phi      logphi " 
! j = 1
! do j = 1, Np
!      write(*, 90) j, centerabsmag(j), phi(j,1), dlog10(phi(j,1))
! enddo
 
! Values of phi for 1st iteration l = 1 have already been established
! Now find values of phi for bins k = 1, 2, . . ., Np
! for iterations l = 2, 3, 4, etc.
! Both j and k refer to the luminosity bin number (2 different sums)
! i refers to the the ith galaxy.
! print *,"  "


!*******************************************************************************
! This section of code is non-essential, but it has been included as a precaution
! to make sure that calculated values of phi do not 'blow up'
! as a result of denominators being equal to zero in Eq. 44.

 badbin = 0
 do k = 1, Np
      count1 = 0
      count2 = 0
      count3 = 0
      do i = 1, ngalaxies
         if ((absmagmax(i)-deltaM/2.0d0) > centerabsmag(k)) then
            H = 1.0d0
            count1 = count1 + 1
         else if ((absmagmax(i)+deltaM/2.0d0) <= centerabsmag(k)) then
            H = 0.0d0
            count2 = count2 + 1
         else
            H = ((absmagmax(i)-centerabsmag(k))/deltaM + 0.5d0)
            count3 = count3 + 1
         endif
       end do
!       print *, " "
!       print *, "k = ", k
!       print *, "H = 1:", count1
!       print *, "H = (Mlim - Mk)/deltaM + 0.5:", count3
!       print *, "H = 0:", count2
       if (count2 == Np) then
          badbin = badbin + 1
       endif
 end do

 if (badbin == Np) then 
      warningflagH = 1.0d0
      print *, "Danger!"
      print *, "None of the Np bins had nonzero values of&
&  the window function H"
 endif

! badbin = 0
! do k = 1, Np
!      count1 = 0
!      count2 = 0
!      do i = 1, ngalaxies
!         if (((centerabsmag(k)-deltaM/2.0d0) <= absmag(i)) &
! & .AND. (absmag(i) <= (centerabsmag(k)+deltaM/2.0d0))) then
!            W = 1.0d0
!            count1 = count1 + 1
!         else 
!            W = 0.0d0
!            count2 = count2 + 1
!         endif
!       end do
!       print *, " "
!       print *, "k = ", k
!       print *, "W = 1:", count1
!       print *, "W = 0:", count2
!       if (count1 == 0) then 
!          badbin = badbin + 1
!       endif
! end do
  
! if (badbin > 0) then 
!      warningflagW = 1.0d0
!      print *, "Danger!"
!      print *, "Some of the bins had no nonzero values of&
!&  the window function W"
! endif
!****************************************************************************
! Code calculates the functions H(i,k) and W(k,i) for all possible combinations of i and k

 allocate(Hmatrix(ngalaxies, Np))
 allocate(Wmatrix(Np, ngalaxies))

 
 do i = 1, ngalaxies

      do j = 1, Np
         if ((absmagmax(i)-deltaM/2.0d0) > &
 & centerabsmag(j)) then
              H = 1.0d0
         else if (((absmagmax(i)-deltaM/2.0d0) <= &
 & centerabsmag(j)).AND.((centerabsmag(j)<(absmagmax(i)+deltaM/2.0d0)&
 &))) then
              H = ((absmagmax(i)-centerabsmag(j))/deltaM &
 & + 0.5d0)
         else if ((absmagmax(i) + deltaM/2.0d0)<= &
 & centerabsmag(j)) then
              H = 0.0d0
         endif
         Hmatrix(i,j) = H

         if (((centerabsmag(j)-deltaM/2.0d0) <= absmag(i)) &
 & .AND. (absmag(i) <= (centerabsmag(j)+deltaM/2.0d0))) then
               W = 1.0d0
         else
               W = 0.0d0
         endif
         Wmatrix(j,i) = W
      end do
 end do

! print *, " "
! print *, " "
! do i = 1, 100
!      do k = 1, Np
!         print *, i, k, Wmatrix(i,k)
!      end do
! end do

! Now calculates the updated values of phi
 allocate(DenomofDenom(ngalaxies))
 allocate(NumofDenom(ngalaxies))
 allocate(Numerator(Np))
 allocate(Denominator(Np))

 

      do l = 2, 5  ! lth iteration
         do k = 1, Np  ! kth bin

! Calculates overall denominator (as function of i) in Eq. 44
            sum = 0.0d0
            do i = 1, ngalaxies  ! ith galaxy
      
! Calculates denominator of denominator (as function of i) in Eq. 44
               subsum = 0.0d0
               do j = 1, Np
                  subsum = subsum + phi(j,l-1)*Hmatrix(i,j)*deltaM
               end do
                  DenomofDenom(i) = subsum

                  NumofDenom(i) = Hmatrix(i,k) 

! Inserted the line below to keep sum from "blowing up"
                if (DenomofDenom(i) /= 0.0d0) then
                   sum = sum + NumofDenom(i)/DenomofDenom(i)
                endif
             end do

! Finally obtain the overall denominator of Eq. 44
             if (sum /= 0.0d0) then 
                Denominator(k) = sum
!                    print *, "Denominator(k): ", k, Denominator(k)
             else
                print *, "WARNING:  denominator diverges for k =", k
             endif

 ! Calculates numerator of Eq. 44 (as function of bin k)
 !                print *, " "
 !                print *, " "
             sum = 0.0d0
             do i = 1, ngalaxies
                sum = sum + Wmatrix(k,i)
             end do
!                  print *, count1, count2

! Finally obtain the numerator for Eq. 2.12
             Numerator(k) = sum
!                  print *, "Num(k), Denom(k)", Numerator(k), &
!& Denominator(k)
!                  print *, Numerator(k)
!                  print *, " "



! Calculates updated value of phi for the kth bin
                  phi(k,l) = Numerator(k)/Denominator(k)/deltaM
              end do
          end do
 
print *, " "
print *, " "
print *, "These are the iterated values for the kth bin"
print *, "Number in far left column = k"

print *, "Number in second column from left is center value of&
 & abs. mag. bin."
print *, "Other #s are iterated phi values."
      k = 1
      do k = 1, Np
            print *,  k, centerabsmag(k), phi(k,1),phi(k,2), &
 &  phi(k,3), phi(k,4),phi(k,5)
      end do

! ****************************************************************************************************
! Prints out values of cummulative version of luminosity function; can comment out if you don't want.
! sum = 0.0d0
! print *, " "
! print *, "Cummulative Phi(M) . . ."
! print *, "  "
! print *, "        Bin #        Abs. Mag.        &
! &     log10 Phi(M)_cumm"
! do k = 1, Np
!      sum = sum + phi(k,5)*deltaM
!      print *, k, centerabsmag(k), dlog10(sum)
! end do



!****************************************************************************************************
! Code finds the selection function S(z)
! print *, " "
! print *, " "
!
!! Code integrates phi(M) from Mlower to Mupper to
!! obtain denominator of Stephen Murray's eqn. 2.9.
! sum = 0.0d0
! do k = 1, Np
!      sum = sum + phi(k,5)*deltaM
!!      print *, k, phi(k,5), phi(k,5)*deltaM, sum
! end do
! bottom = sum
! print *, " "
! print *, "Denominator of Steven Murray's Eqn. 2.9 is ", bottom
! print *, " " 
! 
!
!! Code again integrates phi(M), but upper limit is the 
!! minimum of M2 and Mmax(z), while the lower bound is the
!! maximum of M1 and -infinity (i.e., M1).  This yields
!! numerator of Steven Murray's eqn. 2.9
! 
! deltaz = (0.28d0 - 0.005d0)/Mp
! print *, "Deltaz is ", deltaz
! print *, " "
! print *, "This is a check to make sure that integration of Eq. 2.9 in"
! print *, "Steven Murray's thesis is performed correctly:"
! print *, "If upperlim is less than lsabsmagbin then integration"
! print *, "from that point on will stop.  All remaining values of" 
! print *, "phi*(upperlim-lsbin) should be negative and values of sum"
! print *, "in the final column should no longer increase."
! print *, "Print statements from this section may be"
! print *, "commented out if desired."
! print *, "   "
! print *, "          k         lsbin                   centerbin&
!&                   rsbin                    upperlim           &
!&  phi*(upperlim-lsbin)           sum"
! allocate(SelectFunct(Mp))
! do j = 1, Mp
!      lowerz = 0.005d0 + (j-1)*deltaz
!      upperz = lowerz + deltaz
!      sum = 0.0d0
!      n = 0
!      do i = 1, ngalaxies
!         if ((z(i) >= lowerz) .AND. (z(i) < upperz)) then
!            sum = sum + absmagmax(i)
!            n = n + 1
!         endif
!      end do
!! Mmaxz is the average of the absmagmax(j) values within the redshift bin
!! ****Need to here include section that excludes outliers from average*****
!! ****Can come back and do this later.*****
!      Mmaxz = sum/n
!      print *, "z(center) =", (lowerz + deltaz/2.0d0)
!      upperlim = DMIN1(Mmaxz, Mupper)  ! Since phi(M) was calculated with CENTER of 1st bin at Mlower and
!! CENTER of last bin at Mupper, same procedure is followed here.
!      lowerlim = Mlower
!!     print *, lowerlim, upperlim
!      sum = 0.0d0
!      lsabsmagbin = lowerlim - deltaM/2.0d0
!      rsabsmagbin = lowerlim + deltaM/2.0d0
!      k = 1
!      do while (k <= Np)
!         if (upperlim >= rsabsmagbin) then
!             sum = sum + phi(k,5)*deltaM    ! Uses entire deltaM
!          else if ((upperlim >= lsabsmagbin) .AND. (upperlim <&
! &rsabsmagbin)) then
!             sum = sum + phi(k,5)*(upperlim - lsabsmagbin)  ! Uses only part of deltaM that is <= upperlim
!          endif
!         print *, k, lsabsmagbin, centerabsmag(k), rsabsmagbin, &
! &upperlim, phi(k,5)*(upperlim-lsabsmagbin),sum
!         k = k + 1
!         rsabsmagbin = rsabsmagbin + deltaM
!         lsabsmagbin = lsabsmagbin + deltaM
!      end do
!      print *, " "
!
!       top = sum
!       SelectFunct(j) = top/bottom
! end do
!
! print *, " "
! print *, " "
! print *, "Printing out values of selection function S(z) . . ."
! print *, "         Bin     Center Value of z              S(z)"
! do j = 1, Mp
!      print *, j, ((0.005d0+deltaz/2.0d0)+deltaz*(j-1)), SelectFunct(j)
! end do




 end subroutine
end module