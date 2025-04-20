import React, { useState, useEffect } from 'react';
import ResortCard from './ResortCard';
import ResortMap from './ResortMap';

{
  /*TODO: A function that gets the predicted mountains, this is hard coded*/
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

    {
      place: 'A-Basin',
      distance: 41,
      icon: '/resorticons/Arapahoe-Basin_logo.png',
      iconAlt: 'A-Basin logo',
      endPoint: { lat: 39.634273224137104, lng: -105.87151011854945 },
      encodedPolyline:
        'qt}pFpceeSCb@cBC@{AtAgCbF{CMeDiIaHoJ{BqCzBH~F~EtJfAdNyAiB?mE}E{F{G}BwL`@qn@bSaKG}AeCoA_CsAn@@bB`LzHjJx@`QwAbC~@QdBaRfHiBjEwCpAaFc@gE|CsHfDeJI_KkDqH}K{H}AuBwDcEGgD}ByDAaGSqBeDkH{CiDmCuCtAeLfFoGeBK~BdHfAdPmApK~NlN`L~M`S_@xDcD\\sUwFsXjBgKvAuB|ExBli@mDvXeEa@q@oEiA_ZwEcImTgRe\\gY{Zi_@aM{V_Wmn@gCezBbKyg@`Nad@hUil@~Ful@lE_k@aFod@qKoh@uDaZlFm[Ayd@sAg{@mFs`@`A}j@cDcgAnEgz@dHa{@}@kQaMoZaHeWwIqn@kPkZwa@yl@kM_ImRiBij@oEad@_JyRoFeQmHuNaNsRePySoJyMsQqWww@oTut@sIgRiRaP_TwUsLyj@qOctAyJkh@W}m@nFqkArEeo@w@ar@dEkbAjEmVrImSvW}s@rFyUE}RpG{NnJyJlDaLtFsL`KeOhRms@vIyh@xH{n@hEaY?yRkB{TdAo\\`D{i@qBs[wMu_@yFcPo@kN`DqSKqPeGm`AOmRkFwJTe[tLy\\xDoRiEiUSyNbD_QiH_S}BeI^oH|JeW|DsAnSiDr^qV`TsJdLkMxNsOxLaXtIcW~Kop@tD{TdGuMxKqU`CuTyAcj@pEaa@_@qRaDmXfAcMrHiPnEiKrAmQbAgs@zHq[f\\ka@|H}MjL}g@zAi[wNy\\aVeb@qa@wi@sDwQlKos@xOwbAzBwq@lN{g@fKicAdCaa@_Cme@hHos@dKad@pHcIzDqJz@or@tCmZfHid@jAgb@lA}Ju@{LuLgQmb@e^yn@wd@{J}HSeElCkCjBh@EpHmQpPgOjJeWjBsOP}G~CwIjT}IvJaDtLuGhWaKhKat@|l@cX`Ui[jXsCjMm@vNeE~JgGvGcLlB_EeA}[eN}Lc@a^dLcPhEgHu@oHaEi[aSoJwBeU[m^eB_Ic@iMoAeLqGo\\cUsc@eH_]uGyKwC{VGsa@BqOjCgJjKuKxOuHtDyKfAkYlHgQ|KmQ|P_UWyu@gLgKEyEpAeMpK_e@v^_S|Egk@@agBDgrAGuU{@me@mMibAiXsMj@w]nI{NpAg\\yDeOEsN~CuH_@sNgLg]iQyJFeKnJsMfPwSdJgd@iD}LrDkShRyz@pt@aKjKaGfO}DlImJvHw^dUuVtOuN`KmDjLuV`j@aY~P{JfE}JdCiBb@q@yCS}AaCoRk@{C}FtAsCn@',
      snow: 7,
    },
    {
      place: 'Winter Park',
      distance: 45,
      icon: '/resorticons/winter_park_logo.png',
      iconAlt: 'Winter Park logo',
      endPoint: { lat: 39.89982705581936, lng: -105.7637500794 },
      encodedPolyline:
        'qinrF~zodSjBVp@kBeDo@^aEdDoDjSGpMeCjKuMpQiWpJ_Epx@qNlb@GzSbDxRtHfPp@rUoCb\\`@df@~HfP|Ftm@~WrKiCtAtBiQzDcRiGsMmBe^yBmLuD}LxAf@fElFoEpE^jL`In]pLhLxFnHrI|OhUxGw@`JuItFkBfG|Gj@hPrD^vKuBbRlEnT|^dLnIdDnGxChBzDcB`DuPhH_JhLe@xLxEpEjAo@vBmMyDqKvBeELh@hCnI}@nFz@vJnJrI\\fFkBtDdAnKrTeEnRpDtH~Gs@vI{EtNvBnMjQ|DbIAtN}DnO~HiQfAoOyBaKiD_PaGmGcLkHg@yElGGjKpEjJpMzIvVp@zJvALmAaZu@qFhADzEnWpJ~JxKnj@~Rbb@fOjc@dFfSzI~W|A[c@kFiHmr@{Vu{@kGeWeAuTbGm}@vJa{@zE}v@fBcIhKmK~L_\\`Jib@|L{d@Re[h@cTmBoSjBcb@xF}_@jAiiAnAobBd@sf@xC}X|Ckg@m@qe@bBqOiAmT]{GfCcPhCePcFyQyFmLeGs^wHqs@_Lyk@cBim@vF}fAxAcb@vC}_@i@g_@Di[zBuf@~BmYtHkUbVan@|JwZl@qU|BuOlPiRbGaSfKmNdIyQpFqX|Lmn@zGul@|H}m@{Bkp@nEk\\Bkh@sJu_@uMs_@LmPnCyQgHsfAn@yT{E}K}BgNrEs\\|Mg_@e@cMqEmVzDaQi@uKuJoVnG}XpD{F|Hy@nZkKrSgPdXwMbYy]~Vsq@rQgeAxS{d@pAcS_AgXZc\\bDo_@mD{UhAeYfOm]~@qq@rDq^|FePdLqOvWy]fO}v@oDkWqu@qmAoN{QwB_Jh@{OlWi}AlDag@~@_[nEuPpLch@hIedAq@kd@k@uPtC{XfKcq@~N}TnCsJ`@_`@p@y^xHq`@zAed@xCuYgFgUae@mb@kh@y_@mWkSJcErCeBjClF_LxLyN|McPdDoa@`BsFbFcCfJyO~SeMhe@wpAtfAoYjVcIjImBdOkAdNcEfIeHlGqKdAkRkJwNsEiPVoZrKwQlDaQyH_^}Rq_AcEcSeBem@q_@al@oHiWqHseAq@uJxCoElEkRlWgXpEmYpJs`@t[uUiA}W{Dm]oFmId@_IdEiInHuLrJq[pT}QpCygBHooAIadAgBipAo_@cVcEaPjByi@~Im[}D_OHmP`DuH{AaZ}SmRyHkJrAoZb]kR`GgUuAyNmAqLdGyr@pn@ue@rc@kHnRaTrRuc@rXe\\bUoShh@mGxMkJjG{a@fQ}EhAsAwKaCqRwHdBeB`@',
      snow: 3,
    },
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
    {
      place: 'A-Basin',
      distance: 41,
      icon: '/resorticons/Arapahoe-Basin_logo.png',
      iconAlt: 'A-Basin logo',
      endPoint: { lat: 39.634273224137104, lng: -105.87151011854945 },
      encodedPolyline:
        'qt}pFpceeSCb@cBC@{AtAgCbF{CMeDiIaHoJ{BqCzBH~F~EtJfAdNyAiB?mE}E{F{G}BwL`@qn@bSaKG}AeCoA_CsAn@@bB`LzHjJx@`QwAbC~@QdBaRfHiBjEwCpAaFc@gE|CsHfDeJI_KkDqH}K{H}AuBwDcEGgD}ByDAaGSqBeDkH{CiDmCuCtAeLfFoGeBK~BdHfAdPmApK~NlN`L~M`S_@xDcD\\sUwFsXjBgKvAuB|ExBli@mDvXeEa@q@oEiA_ZwEcImTgRe\\gY{Zi_@aM{V_Wmn@gCezBbKyg@`Nad@hUil@~Ful@lE_k@aFod@qKoh@uDaZlFm[Ayd@sAg{@mFs`@`A}j@cDcgAnEgz@dHa{@}@kQaMoZaHeWwIqn@kPkZwa@yl@kM_ImRiBij@oEad@_JyRoFeQmHuNaNsRePySoJyMsQqWww@oTut@sIgRiRaP_TwUsLyj@qOctAyJkh@W}m@nFqkArEeo@w@ar@dEkbAjEmVrImSvW}s@rFyUE}RpG{NnJyJlDaLtFsL`KeOhRms@vIyh@xH{n@hEaY?yRkB{TdAo\\`D{i@qBs[wMu_@yFcPo@kN`DqSKqPeGm`AOmRkFwJTe[tLy\\xDoRiEiUSyNbD_QiH_S}BeI^oH|JeW|DsAnSiDr^qV`TsJdLkMxNsOxLaXtIcW~Kop@tD{TdGuMxKqU`CuTyAcj@pEaa@_@qRaDmXfAcMrHiPnEiKrAmQbAgs@zHq[f\\ka@|H}MjL}g@zAi[wNy\\aVeb@qa@wi@sDwQlKos@xOwbAzBwq@lN{g@fKicAdCaa@_Cme@hHos@dKad@pHcIzDqJz@or@tCmZfHid@jAgb@lA}Ju@{LuLgQmb@e^yn@wd@{J}HSeElCkCjBh@EpHmQpPgOjJeWjBsOP}G~CwIjT}IvJaDtLuGhWaKhKat@|l@cX`Ui[jXsCjMm@vNeE~JgGvGcLlB_EeA}[eN}Lc@a^dLcPhEgHu@oHaEi[aSoJwBeU[m^eB_Ic@iMoAeLqGo\\cUsc@eH_]uGyKwC{VGsa@BqOjCgJjKuKxOuHtDyKfAkYlHgQ|KmQ|P_UWyu@gLgKEyEpAeMpK_e@v^_S|Egk@@agBDgrAGuU{@me@mMibAiXsMj@w]nI{NpAg\\yDeOEsN~CuH_@sNgLg]iQyJFeKnJsMfPwSdJgd@iD}LrDkShRyz@pt@aKjKaGfO}DlImJvHw^dUuVtOuN`KmDjLuV`j@aY~P{JfE}JdCiBb@q@yCS}AaCoRk@{C}FtAsCn@',
      snow: 7,
    },
    {
      place: 'Winter Park',
      distance: 45,
      icon: '/resorticons/winter_park_logo.png',
      iconAlt: 'Winter Park logo',
      endPoint: { lat: 39.89982705581936, lng: -105.7637500794 },
      encodedPolyline:
        'qinrF~zodSjBVp@kBeDo@^aEdDoDjSGpMeCjKuMpQiWpJ_Epx@qNlb@GzSbDxRtHfPp@rUoCb\\`@df@~HfP|Ftm@~WrKiCtAtBiQzDcRiGsMmBe^yBmLuD}LxAf@fElFoEpE^jL`In]pLhLxFnHrI|OhUxGw@`JuItFkBfG|Gj@hPrD^vKuBbRlEnT|^dLnIdDnGxChBzDcB`DuPhH_JhLe@xLxEpEjAo@vBmMyDqKvBeELh@hCnI}@nFz@vJnJrI\\fFkBtDdAnKrTeEnRpDtH~Gs@vI{EtNvBnMjQ|DbIAtN}DnO~HiQfAoOyBaKiD_PaGmGcLkHg@yElGGjKpEjJpMzIvVp@zJvALmAaZu@qFhADzEnWpJ~JxKnj@~Rbb@fOjc@dFfSzI~W|A[c@kFiHmr@{Vu{@kGeWeAuTbGm}@vJa{@zE}v@fBcIhKmK~L_\\`Jib@|L{d@Re[h@cTmBoSjBcb@xF}_@jAiiAnAobBd@sf@xC}X|Ckg@m@qe@bBqOiAmT]{GfCcPhCePcFyQyFmLeGs^wHqs@_Lyk@cBim@vF}fAxAcb@vC}_@i@g_@Di[zBuf@~BmYtHkUbVan@|JwZl@qU|BuOlPiRbGaSfKmNdIyQpFqX|Lmn@zGul@|H}m@{Bkp@nEk\\Bkh@sJu_@uMs_@LmPnCyQgHsfAn@yT{E}K}BgNrEs\\|Mg_@e@cMqEmVzDaQi@uKuJoVnG}XpD{F|Hy@nZkKrSgPdXwMbYy]~Vsq@rQgeAxS{d@pAcS_AgXZc\\bDo_@mD{UhAeYfOm]~@qq@rDq^|FePdLqOvWy]fO}v@oDkWqu@qmAoN{QwB_Jh@{OlWi}AlDag@~@_[nEuPpLch@hIedAq@kd@k@uPtC{XfKcq@~N}TnCsJ`@_`@p@y^xHq`@zAed@xCuYgFgUae@mb@kh@y_@mWkSJcErCeBjClF_LxLyN|McPdDoa@`BsFbFcCfJyO~SeMhe@wpAtfAoYjVcIjImBdOkAdNcEfIeHlGqKdAkRkJwNsEiPVoZrKwQlDaQyH_^}Rq_AcEcSeBem@q_@al@oHiWqHseAq@uJxCoElEkRlWgXpEmYpJs`@t[uUiA}W{Dm]oFmId@_IdEiInHuLrJq[pT}QpCygBHooAIadAgBipAo_@cVcEaPjByi@~Im[}D_OHmP`DuH{AaZ}SmRyHkJrAoZb]kR`GgUuAyNmAqLdGyr@pn@ue@rc@kHnRaTrRuc@rXe\\bUoShh@mGxMkJjG{a@fQ}EhAsAwKaCqRwHdBeB`@',
      snow: 3,
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

  const [selectedMountain, setSelectedMountain] = useState<any | null>(null);

  useEffect(() => {
    if (mountains && mountains.length > 0) {
      setSelectedMountain(mountains[0]);
    }
  }, [mountains, startpoint]);

  const start = startpoint ? startpoint : [40.0189728, -105.2747406];
  if (!selectedMountain) return <p>Loading resort map...</p>;
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
