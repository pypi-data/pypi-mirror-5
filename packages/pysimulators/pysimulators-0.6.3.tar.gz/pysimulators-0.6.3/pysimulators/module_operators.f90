module operators

    use module_pointingmatrix
    implicit none

    ! <itype=4,4,4,8,8,8>
    ! <mtype=4,4,8,4,4,8>
    ! <vtype=4,8,8,4,8,8>

contains

    subroutine fsr_pT1_i4_m4_v4(matrix, pT1, ncolmax, ninput,&
                                    noutput)
        integer, parameter          :: s = 4 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i4_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*4, intent(inout) :: pT1(0:noutput-1)
        integer*4 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%value
            end do
        end do
        !$omp end parallel do

    end subroutine


    subroutine fsr_pT1_i4_m4_v8(matrix, pT1, ncolmax, ninput,&
                                    noutput)
        integer, parameter          :: s = 4 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i4_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*4 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%value
            end do
        end do
        !$omp end parallel do

    end subroutine


    subroutine fsr_pT1_i4_m8_v8(matrix, pT1, ncolmax, ninput,&
                                    noutput)
        integer, parameter          :: s = 4 + 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i4_m8), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*4 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%value
            end do
        end do
        !$omp end parallel do

    end subroutine


    subroutine fsr_pT1_i8_m4_v4(matrix, pT1, ncolmax, ninput,&
                                    noutput)
        integer, parameter          :: s = 8 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i8_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*4, intent(inout) :: pT1(0:noutput-1)
        integer*8 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%value
            end do
        end do
        !$omp end parallel do

    end subroutine


    subroutine fsr_pT1_i8_m4_v8(matrix, pT1, ncolmax, ninput,&
                                    noutput)
        integer, parameter          :: s = 8 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i8_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*8 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%value
            end do
        end do
        !$omp end parallel do

    end subroutine


    subroutine fsr_pT1_i8_m8_v8(matrix, pT1, ncolmax, ninput,&
                                    noutput)
        integer, parameter          :: s = 8 + 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i8_m8), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*8 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%value
            end do
        end do
        !$omp end parallel do

    end subroutine




    subroutine fsr_rot3d_pT1_i4_m4_v4(matrix, pT1, ncolmax,  &
                                          ninput, noutput)
        integer, parameter          :: s = 4 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i4_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*4, intent(inout) :: pT1(0:noutput-1)
        integer*4 :: col
        integer*8 :: i, j

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%r11
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pT1_i4_m4_v8(matrix, pT1, ncolmax,  &
                                          ninput, noutput)
        integer, parameter          :: s = 4 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i4_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*4 :: col
        integer*8 :: i, j

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%r11
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pT1_i4_m8_v8(matrix, pT1, ncolmax,  &
                                          ninput, noutput)
        integer, parameter          :: s = 4 + 3 * 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i4_m8), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*4 :: col
        integer*8 :: i, j

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%r11
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pT1_i8_m4_v4(matrix, pT1, ncolmax,  &
                                          ninput, noutput)
        integer, parameter          :: s = 8 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i8_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*4, intent(inout) :: pT1(0:noutput-1)
        integer*8 :: col
        integer*8 :: i, j

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%r11
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pT1_i8_m4_v8(matrix, pT1, ncolmax,  &
                                          ninput, noutput)
        integer, parameter          :: s = 8 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i8_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*8 :: col
        integer*8 :: i, j

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%r11
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pT1_i8_m8_v8(matrix, pT1, ncolmax,  &
                                          ninput, noutput)
        integer, parameter          :: s = 8 + 3 * 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i8_m8), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(inout) :: pT1(0:noutput-1)
        integer*8 :: col
        integer*8 :: i, j

        !$omp parallel do private(col)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                !$omp atomic update
                pT1(col) = pT1(col) + matrix(j,i)%r11
            end do
        end do
        !$omp end parallel do

    end subroutine




    subroutine fsr_pTx_pT1_i4_m4_v4(matrix, input, pTx, pT1, &
                                    ncolmax, ninput, noutput)
        integer, parameter          :: s = 4 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i4_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*4, intent(in)    :: input(ninput)
        real*4, intent(inout) :: pTx(0:noutput-1)
        real*4, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*4 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%value
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_pTx_pT1_i4_m4_v8(matrix, input, pTx, pT1, &
                                    ncolmax, ninput, noutput)
        integer, parameter          :: s = 4 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i4_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*4 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%value
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_pTx_pT1_i4_m8_v8(matrix, input, pTx, pT1, &
                                    ncolmax, ninput, noutput)
        integer, parameter          :: s = 4 + 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i4_m8), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*8 :: val
        integer*4 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%value
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_pTx_pT1_i8_m4_v4(matrix, input, pTx, pT1, &
                                    ncolmax, ninput, noutput)
        integer, parameter          :: s = 8 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i8_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*4, intent(in)    :: input(ninput)
        real*4, intent(inout) :: pTx(0:noutput-1)
        real*4, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*8 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%value
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_pTx_pT1_i8_m4_v8(matrix, input, pTx, pT1, &
                                    ncolmax, ninput, noutput)
        integer, parameter          :: s = 8 + 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i8_m4), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*8 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%value
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_pTx_pT1_i8_m8_v8(matrix, input, pTx, pT1, &
                                    ncolmax, ninput, noutput)
        integer, parameter          :: s = 8 + 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElement_i8_m8), intent(in) ::                 &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*8 :: val
        integer*8 :: col
        integer*8 :: i, j        

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%value
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine




    subroutine fsr_rot3d_pTx_pT1_i4_m4_v4(matrix, input, pTx,&
                                          pT1, ncolmax, ninput, noutput)
        integer, parameter          :: s = 4 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i4_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*4, intent(in)    :: input(ninput)
        real*4, intent(inout) :: pTx(0:noutput-1)
        real*4, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*4 :: col
        integer*8 :: i, j

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%r11
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pTx_pT1_i4_m4_v8(matrix, input, pTx,&
                                          pT1, ncolmax, ninput, noutput)
        integer, parameter          :: s = 4 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i4_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*4 :: col
        integer*8 :: i, j

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%r11
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pTx_pT1_i4_m8_v8(matrix, input, pTx,&
                                          pT1, ncolmax, ninput, noutput)
        integer, parameter          :: s = 4 + 3 * 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i4_m8), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*8 :: val
        integer*4 :: col
        integer*8 :: i, j

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%r11
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pTx_pT1_i8_m4_v4(matrix, input, pTx,&
                                          pT1, ncolmax, ninput, noutput)
        integer, parameter          :: s = 8 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i8_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*4, intent(in)    :: input(ninput)
        real*4, intent(inout) :: pTx(0:noutput-1)
        real*4, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*8 :: col
        integer*8 :: i, j

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%r11
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pTx_pT1_i8_m4_v8(matrix, input, pTx,&
                                          pT1, ncolmax, ninput, noutput)
        integer, parameter          :: s = 8 + 3 * 4
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i8_m4), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*4 :: val
        integer*8 :: col
        integer*8 :: i, j

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%r11
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine



    subroutine fsr_rot3d_pTx_pT1_i8_m8_v8(matrix, input, pTx,&
                                          pT1, ncolmax, ninput, noutput)
        integer, parameter          :: s = 8 + 3 * 8
        integer*8, intent(in)       :: ncolmax
        integer*8, intent(in)       :: ninput
        integer*8, intent(in)       :: noutput
        !f2py integer*1, intent(in) :: matrix(ncolmax*ninput*s)
        type(PointingElementRot3d_i8_m8), intent(in) ::            &
            matrix(ncolmax, ninput)
        real*8, intent(in)    :: input(ninput)
        real*8, intent(inout) :: pTx(0:noutput-1)
        real*8, intent(inout) :: pT1(0:noutput-1)
        real*8 :: val
        integer*8 :: col
        integer*8 :: i, j

        !$omp parallel do private(col, val)
        do i = 1, ninput
            do j = 1, ncolmax
                col = matrix(j,i)%index
                if (col < 0) exit
                val = matrix(j,i)%r11
                !$omp atomic update
                pTx(col) = pTx(col) + val * input(i)
                !$omp atomic update
                pT1(col) = pT1(col) + val
            end do
        end do
        !$omp end parallel do

    end subroutine




end module operators
