module luminosity
    implicit none

    real(8), parameter :: sollum = 3.839d26  ! Luminosity of sun (in watts)
    real(8), parameter :: solabsmag = 4.67d0  ! Need to double check this value; not sure what band this is for.
    real(8) :: Mupper = -11.0d0  ! Upper abs. mag. limit of survey
    real(8) :: Mlower = -24.0d0  ! Lower abs. mag. limit of survey

    real(8) :: minmagr, maxmagr, deltaM

    contains
!magr,lumdist,kcorr
    subroutine lumfunc(ngalaxies,Np,absmag,kcorr,lumdist,magr,maxiter,last_phi,bins)
        implicit none
        ! Subroutine uses redshift and absolute magnitude data
        ! to obtain the luminosity function as a function of
        ! absolute magnitude
        ! See "Application of the Information Criterion to the 
        ! Estimation of Galaxy Luminosity Function"
        ! by Tsutomu T. Takeuchi

        !The following are input vectors of galaxy info
        real(8), intent(in) :: magr(ngalaxies)
        real(8), intent(in) :: kcorr(ngalaxies),lumdist(ngalaxies)
        real(8), intent(in) ::  absmag(ngalaxies)

        !The following is the input number of luminosity bins and maximum
        !number of iterations wanted
        integer, intent(in) :: Np, maxiter, ngalaxies

        real(8), intent(out) :: last_phi(Np)
        real(8), intent(out) :: bins(Np)
        !The following is the output luminosity function
        real(8)  :: phi(Np,maxiter)

        !Output number of iterations actually used
        !integer, intent(out) :: iter

        !Several local arrays.
        !real(8), allocatable :: absmagmax(:), absmagmin(:)
        integer, allocatable :: W(:)

        real(8), allocatable :: Denom
        real(8), allocatable :: DenomofDenom, NumofDenom ! Takeuchi's Eqn. 44


        integer:: i, j, k, l

        ! Code now determines the largest (dimmest) apparent mag.
        ! and smallest (brightest) apparent mag.
        ! values of magr - THESE SHOULD BE SET BY THE SURVEY ITSELF (look at a paper..)
         minmagr = minval(magr)
         maxmagr = maxval(magr)

        write(*,*) "Minimum mag_r", minmagr
        write(*,*) "Maximum mag_r", maxmagr
        write(*,*) "Minimum AbsMag: ", minval(absmag)
        write(*,*) "maximum AbsMag: ", maxval(absmag)

        Mupper = min(Mupper,maxval(absmag))
        Mlower = max(Mlower, minval(absmag))
        write(*,*) "AbsMag bounds now", Mlower , Mupper


        ! Code now assigns the initial trial values of
        ! the luminosity function phi for each magnitude bin
        ! The number of magnitude bins is Np
        ! The initial trial luminosity function will be obtained by counting
        ! the number of galaxies in each of the Np magnitude bins
         allocate(W(Np))

        ! Counts the galaxies within each abs. mag. bin and uses the counts
        ! to obtain an initial guess for phi for each bin
         phi = 0.d0
         deltaM = (Mupper-Mlower)/Np
         do k=1,Np
            bins(k) = Mlower + (k-0.5)*deltaM
         end do
         write(*,*) "deltaM = ", deltaM
         call sum_W(Np,ngalaxies,absmag,W)
         phi(:,1) = W

         !Warn user if any values of H,W are 0
         do k=1,Np
            if (W(k) == 0)then
                write(*,*) "Warning: W at k=",k, "is 0"
            end if
         end do




         do l = 2, maxiter  ! lth iteration
            do k = 1, Np  ! kth bin

                Denom = 0.d0
                !Denominator
                do i = 1, ngalaxies
                    NumofDenom = H(absmagmax(lumdist(i),kcorr(i))-bins(k))

                    ! Calculates denominator of denominator (as function of i) in Eq. 44
                    DenomofDenom = 0.0d0
                    do j = 1, Np
                        DenomofDenom = DenomofDenom + phi(j,l-1)*H(absmagmax(lumdist(i),kcorr(i))-bins(j))*deltaM
                    end do

                    if (DenomofDenom == 0.d0)then
                        write(*,*) "Warning: phi_k*H at k,j = ",k,j," is 0"
                    end if
                    Denom = Denom + NumofDenom/DenomofDenom
                end do

                if (denom == 0.d0)then
                    write(*,*) "Warning: Denominator 0 at k=",k

                end if

                ! Calculates updated value of phi for the kth bin
                phi(k,l) = W(k)/Denom/deltaM
            end do
        end do

        last_phi = phi(:,maxiter)
    end subroutine lumfunc

    function absmagmax(lumdist,kcorr)
        real(8) :: absmagmax
        real(8), intent(in) :: lumdist, kcorr
        absmagmax = maxmagr -5.0d0*dlog10(lumdist)-25.0d0-kcorr
    end function

    subroutine sum_W(Np,ngalaxies,absmag,W)
        integer, intent(in) :: Np, ngalaxies
        real(8), intent(in) :: absmag(ngalaxies)
        integer, intent(out) :: W(Np)

        integer :: bin,i
        W = 0
        do i=1,ngalaxies
            bin = floor((absmag(i)-Mlower)/deltaM) + 1
            if (bin .GT. 0 .and. bin .le. Np)then
                W(bin) = W(bin)+1
            end if
         end do

    end subroutine

    function H(entry)
        real(8) :: H
        real(8) :: entry

        if(entry .gt. deltaM/2)then
            H = 1.d0
        else if(entry.lt.deltaM/2)then
            H = 0.d0
        else
            H = entry/deltaM + 0.5d0
        end if
    end function

end module luminosity

