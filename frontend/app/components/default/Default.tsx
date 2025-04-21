import React, { useState, useEffect } from 'react';
import ResortCardDefault from './ResortCardDefault';
import ResortMapDefault from './ResortMapDefault';

{
  /*TODO: A function that gets the predicted mountains, this is hard coded*/
}

interface DefaultProps {
  defaultData: any[] | null;
}

const getPredictedMountains = () => {
  return [
    {
      place: 'Copper Mountain',
      distance: 40,
      icon: '/resorticons/copper_logo.png',
      iconAlt: 'Copper logo',
      endPoint: { lat: 39.50323660321131, lng: -106.15144380943651 },
      encodedPolyline:
        '_cbpF~v{fS{BaQtA_NRmI{HmHuDoGyBIaFnDiDL_BJmK|BiD`Aw]bHkR|CqF]{L_H_Sg\\_GqFqKeCgSnGgTjPaR`E_LmD}LsK{d@kK}]iS}Q}TsPuGoQSoRiNeQyb@oP{c@{TcPwt@eRcKaGyI}Mem@mdAoo@ql@uR_\\_WaRsU{^{MwKcFuAcWt@eQ^_IcB{QkN{Pud@_Rsn@sKsZsZod@sRkh@kMeh@{AcZiI_SeMmVkDkRmLkXkEqg@i@sXaFcZwPsg@gOg\\gLw`@uYec@oZ_S{MiRmB}JsBgu@aNk`@m@ir@Paa@wJuj@E_eA@{_A{Ai}@qKkXcB{WiB{_@sQcV__@e_@u[s_@aN}WmWwn@aBes@o@qfA`Jyd@be@_tAxMixA{E{d@oKmh@}D{YjFe\\sAiaBmFi`@fAgj@iDsgAzDaw@lHu{@q@mT_Vuq@wIgo@mPsZka@ml@sLcImRoB{i@kEkd@yIye@_PaXgWi^wRuMaQuIoTeWu{@kTin@eQmO{UeWmL_j@oH}n@uMsy@iE}h@bEey@bHm{AH{kA|Bgg@jEkWpSkf@rUyw@KmRdGeOvJ_KrD}KnFyL|JuNpHsTjN{s@zG{j@xKeq@gBog@x@i]fDqi@kBk\\iM}^gG_Qw@uM`Dgd@qGiaAGeSkFqJHkZnLc]fEcSyDgTi@qOhDqQ_HmRgBeSpJ{VxXwFj_@{VdTyJfLiMfN}N`McXlIeVhK{l@xEsYfG_NxKmUbCwSwAek@jEg`@U}RcD_X~@wMdH_P~EuKtA_P~@et@rHw[~[ma@lIgNxKue@vB}\\oNe]}To`@_b@uj@uEcR~RyqAfHee@vB}p@fNeh@pIuv@dEum@_Cge@vGwq@bK{e@xNuTbA{r@zLi_AlBa|@mLsQoUiTca@kZ{X{R}KoI[kE~BmCtB\\?xHmQpPsNdJkVlB}PTuGpCoIxSuIlJsDfL}G|XeG~Gav@vn@{u@jo@cDnMi@rNuLxSeLbCoE_Ac[cN_Nm@m]zKaPpE_RaFwZcS_\\sC{m@yCoMoA}KqG{Z}Sk^aHuc@wHkK{CmVKcb@@aPbC}IpJaKnO}T`HaX|F_SzKePhQ}Sn@mv@gLySTgN`Lub@h]kUvGqk@@_gBDgrAGsU{@md@_MiaAoXuNZo[tHyPtB}[oDyPQuLjCyIAeOkLw\\gQoJKgJbH_OjRaRhJge@sCcMjCcTzR}z@xt@}J|JeGjOcKzOkc@lX_W|OmNjJ_ErLuVjj@iX|PcKnEkKhCgCl@q@qFoBuOs@aGqEdAkE`A',
      snow: 6,
    },
  ];
};

const startpoint = { lat: 40.0158361, lng: -105.2792329 };

const Default: React.FC<DefaultProps> = ({ defaultData }) => {
  const [mountains, setMountains] = useState<any[]>([]);
  const [selectedMountain, setSelectedMountain] = useState<any | null>(null);

  // Initialize data once defaultData is loaded
  useEffect(() => {
    const data =
      defaultData && defaultData.length > 0
        ? defaultData
        : getPredictedMountains();
    setMountains(data);
    setSelectedMountain(data[0]);
  }, [defaultData]);

  if (!defaultData || defaultData.length === 0) {
    return (
      <div className="flex flex-col items-center md:flex-row">
        <ResortMapDefault startPoint={startpoint} />
        <div className="flex flex-col overflow-y-auto max-h-[500px] w-80 p-2 border-l">
          Loading resorts...
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center md:flex-row">
      <ResortMapDefault startPoint={selectedMountain.endPoint} />
      <div className="flex flex-col max-h-[500px] w-80 p-2 ">
        <p className="text-white text-xl font-semibold py-2">All resorts:</p>
        <div className=" max-h-[500px] overflow-y-auto">
          {defaultData.map((mountain, index) => (
            <div
              key={index}
              onClick={() => setSelectedMountain(mountain)}
              className="cursor-pointer"
            >
              <ResortCardDefault
                place={mountain.place}
                icon={mountain.icon}
                iconAlt={mountain.iconAlt}
                snow={mountain.snow}
              />
            </div>
          ))}
        </div>{' '}
      </div>
    </div>
  );
};

export default Default;
