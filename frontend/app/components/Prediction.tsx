import React, { useState } from 'react';
import ResortCard from './ResortCard';
import ResortMap from './ResortMap';

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

interface PredictionProps {
  predictionData: any[] | null;
  startpoint: any[];
}
const Prediction: React.FC<PredictionProps> = ({
  predictionData,
  startpoint,
}) => {
  const mountains =
    predictionData && predictionData.length > 0
      ? predictionData
      : getPredictedMountains();

  const [selectedMountain, setSelectedMountain] = useState(mountains[0]);
  const start = startpoint ? startpoint : [40.0189728, -105.2747406];

  console.log(selectedMountain);

  if (predictionData === null) {
    console.log('Null');

    return (
      <div className="flex flex-row">
        <ResortMap startPoint={startpoint} />
        <div className="flex flex-col overflow-y-auto max-h-[500px] w-80 p-2 border-l border-gray-300 text-lg ">
          Finding your perfect match!
        </div>
      </div>
    );
  }
  if (predictionData.length === 0) {
    console.log('empty');

    return (
      <div className="flex flex-row">
        <ResortMap startPoint={startpoint} />
        <div className="flex flex-col overflow-y-auto max-h-[500px] w-80 p-2 border-l border-gray-300 text-white text-lg">
          No match found. Try adjusting your preferences!
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-row">
      <ResortMap
        startPoint={start}
        endPoint={selectedMountain.endPoint}
        encodedPolyline={selectedMountain.encodedPolyline}
      />
      <div className="flex flex-col overflow-y-auto max-h-[500px] w-80 p-2 border-l border-gray-300">
        {mountains.map((mountain, index) => (
          <div
            key={index}
            onClick={() => setSelectedMountain(mountain)}
            className="cursor-pointer"
          >
            <ResortCard
              place={mountain.place}
              distance={mountain.distance}
              icon={mountain.icon}
              iconAlt={mountain.iconAlt}
              snow={mountain.snow}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Prediction;
