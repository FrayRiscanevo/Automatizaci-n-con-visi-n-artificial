MODULE FivePointsSocket

    VAR socketdev sd_listen;
    VAR socketdev sd_client;

    VAR string rxmsg := "";

    VAR num offX := 0;
    VAR num offY := 0;
    VAR num offZ := 0;

    VAR robtarget pBase;
    VAR robtarget pTarget;

    ! -------- HOME SEGURO (ejemplo) --------
    ! Luego lo puedes ajustar con un jointtarget real del robot
    CONST jointtarget jSafeHome := [[0,-5,-5,0,5,0],
                                    [9E9,9E9,9E9,9E9,9E9,9E9]];

    PROC main()

        TPWrite "Moviendo a HOME SEGURO...";
        MoveAbsJ jSafeHome, v30, fine, tool0;

        ! Tomamos la pose cartesiana desde esa postura segura
        pBase := CRobT(\Tool:=tool0 \WObj:=wobj0);

        ! ----- Configuración del socket servidor -----
        SocketCreate sd_listen;
        SocketBind   sd_listen, "127.0.0.1", 5000;
        SocketListen sd_listen;

        TPWrite "Esperando conexión de Python...";
        SocketAccept sd_listen, sd_client;
        TPWrite "Python conectado.";

        WHILE TRUE DO

            rxmsg := "";
            SocketReceive sd_client\Str:=rxmsg;
            TPWrite "Crudo: " + rxmsg;

            ! Parsear "X,Y,Z" (offsets en mm)
            ParseXYZ rxmsg, offX, offY, offZ;

            TPWrite "Offset X (mm): "\Num:=offX;
            TPWrite "Offset Y (mm): "\Num:=offY;
            TPWrite "Offset Z (mm): "\Num:=offZ;

            ! Construir punto objetivo = base + offset
            pTarget := pBase;
            pTarget.trans.x := pBase.trans.x + offX;
            pTarget.trans.y := pBase.trans.y + offY;
            pTarget.trans.z := pBase.trans.z + offZ;

            TPWrite "Moviendo al nuevo punto...";
            MoveL pTarget, v30, fine, tool0;

            ! Si quieres que cada punto sea relativo al anterior:
            pBase := pTarget;

            WaitTime 0.1;

        ENDWHILE

        SocketClose sd_client;
        SocketClose sd_listen;

    ENDPROC

    !-----------------------------------------------------
    ! ParseXYZ: separa "a,b,c" en 3 números (X,Y,Z)
    !-----------------------------------------------------
    PROC ParseXYZ(string s, VAR num X, VAR num Y, VAR num Z)
        VAR num pos;
        VAR bool ok;
        VAR string t;

        ! ---- X ----
        pos := StrFind(s, 1, ",");
        IF pos = 0 THEN
            TPWrite "Error formato: falta coma 1";
            RETURN;
        ENDIF
        t := StrPart(s, 1, pos - 1);
        ok := StrToVal(t, X);

        ! ---- resto "Y,Z" ----
        s := StrPart(s, pos + 1, StrLen(s) - pos);

        ! ---- Y ----
        pos := StrFind(s, 1, ",");
        IF pos = 0 THEN
            TPWrite "Error formato: falta coma 2";
            RETURN;
        ENDIF
        t := StrPart(s, 1, pos - 1);
        ok := StrToVal(t, Y);

        ! ---- Z ----
        t := StrPart(s, pos + 1, StrLen(s) - pos);
        ok := StrToVal(t, Z);

    ENDPROC

ENDMODULE