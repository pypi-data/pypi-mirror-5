
#ifndef FLUIDCLASS_H
#define FLUIDCLASS_H

#include <list>
#include <map>
#include <string>
#include <exception>
#include <vector>

#include "CPExceptions.h"
#include "CoolPropTools.h"
#include "Helmholtz.h"
#include "TTSE.h"

class Fluid;

struct OtherParameters
{
	double molemass, Ttriple, ptriple, accentricfactor, R_u;
};
struct CriticalStruct
{
	double rho, T, p, v;
};
struct FluidLimits
{
	double Tmin, Tmax, pmax, rhomax;	
};

struct SatLUTStruct
{
	std::vector<double> T,rhoL,rhoV,p,hL,hV,sL,sV,tau,logp;
	std::vector<double> T_reversed,rhoL_reversed,rhoV_reversed,p_reversed,hL_reversed,hV_reversed,sL_reversed,sV_reversed,tau_reversed,logp_reversed;
	int N;
	bool built;
	enum flags{ iT,iP,iHL,iHV,iDL,iDV,iSL,iSV};
};

class CriticalSplineStruct_T
{
public:
	CriticalSplineStruct_T(){};
	CriticalSplineStruct_T(double Tend, double rhoendL, double rhoendV, double drhoLdT_sat, double drhoVdT_sat);
	/// Interpolate within the spline to get the density
	/// @param pFluid Pointer to fluid of interest
	/// @param phase Integer for phase (0=liquid, 1 = vapor)
	/// @param T Tempeature [K]
	double interpolate_rho(Fluid* pFluid, int phase, double T);

	/// The last temperature for which the conventional methods can be used
	double Tend;
	/// Saturated liquid density at the last temperature for which the conventional methods can be used
	double rhoendL;
	/// Saturated vapor density at the last temperature for which the conventional methods can be used
	double rhoendV;
	/// Derivative of density w.r.t. temperature along the saturated liquid curve
	double drhoLdT_sat;
	/// Derivative of density w.r.t. temperature along the saturated vapor curve
	double drhoVdT_sat;
};

class AncillaryCurveClass
{
public:
	// Default Constructor
	AncillaryCurveClass(){built = false;};
	// Constructor with values
	AncillaryCurveClass(Fluid *pFluid, std::string Output){built = false; update(pFluid,Output);};
	void update(Fluid *pFluid, std::string Output);
	std::vector<double> xL,yL,xV,yV;
	int build(int N);
	long iOutput;
	Fluid * pFluid;
	double interpolateL(double T);
	double interpolateV(double T);
	double reverseinterpolateL(double y);
	double reverseinterpolateV(double y);
	bool built;
};

struct OnePhaseLUTStruct
{
	std::vector< std::vector<double> > hmat,rhomat,cpmat,cp0mat, smat,cvmat,umat,viscmat,kmat,pmat,dpdTmat;
	std::vector<double> Tvec,pvec;
	double Tmin,Tmax,pmin,pmax;
	int nT,np;
	bool built,forcebuild;
};

/// Rebuild the constants
void rebuild_CriticalSplineConstants_T();

struct BibTeXKeysStruct
{
	std::string EOS;
	std::string CP0;
	std::string VISCOSITY;
	std::string CONDUCTIVITY;
	std::string ECS_LENNARD_JONES;
	std::string ECS_FITS;
	std::string SURFACE_TENSION;
	
};

/// Fluid is the abstract base class that is employed by all the other fluids
class Fluid
{
	protected:
		std::string name; /// The name of the fluid
		std::string REFPROPname; /// The REFPROP-compliant name if REFPROP-"name" is not a compatible fluid name.  If not included, "name" is assumed to be a valid name for REFPROP
		std::vector <std::string> aliases; /// A list of aliases of names for the Fluid, each element is a std::string instance
		std::string ECSReferenceFluid; /// A string that gives the name of the fluids that should be used for the ECS method for transport properties
		
		std::string EOSReference; /// A std::string that contains a reference for thermo properties for the fluid
		std::string TransportReference; /// A std::string that contains a reference for the transport properties of the fluid
		bool isPure; /// True if it is a pure fluid, false otherqwise

		// The structures that hold onto ancillary data for the fluid
		AncillaryCurveClass *h_ancillary;
		AncillaryCurveClass *s_ancillary;
		AncillaryCurveClass *cp_ancillary;
		AncillaryCurveClass *drhodT_p_ancillary;

		/// Obtain a guess value for the density of the fluid for a given set of temperature and pressure
		/// @param T Temperature [K]
		/// @param p Pressure [kPa(abs)]
		double _get_rho_guess(double T, double p); 

		// The boundaries for the TTSE
		double hmin_TTSE, hmax_TTSE, pmin_TTSE, pmax_TTSE;
		unsigned int Nsat_TTSE, Nh_TTSE, Np_TTSE;
    public:
		SatLUTStruct SatLUT; /// The private Saturation lookup structure

		BibTeXKeysStruct BibTeXKeys;

		std::vector <phi_BC*> phirlist; /// A list of instances of the phi_BC classes for the residual Helmholtz energy contribution
		std::vector <phi_BC*> phi0list; /// A list of instances of the phi_BC classes for the ideal-gas Helmholtz energy contribution

		/// Constructor for the Fluid class.  This is an abstract base class that 
		/// is not meant to be instantiated directly.  Rather it should be subclassed
		/// to implement new fluids.  Examples of this behavior are the R134aClass or the 
		/// R290Class classes.
		Fluid(){
			params.R_u=8.314472; /// Default molar gas constant [kJ/kmol/K]
			isPure=true;  /// true if fluid is one-component pure fluid, false otherwise

			// Default parameters for TTSE - others are set in post-load() function
			built_TTSE_LUT = false;
			enabled_TTSE_LUT = false;
			Nsat_TTSE = 400;
			Nh_TTSE = 200;
			Np_TTSE = 200;
			hmin_TTSE = _HUGE;
			hmax_TTSE = _HUGE;
			pmin_TTSE = _HUGE;
			pmax_TTSE = _HUGE;
			enable_writing_tables_to_files = true;
			CriticalSpline_T.Tend = _HUGE;
				
			preduce = &crit; /// pointer to the reducing parameters
			h_ancillary = NULL;
			s_ancillary = NULL;
			cp_ancillary = NULL;
			drhodT_p_ancillary = NULL;
			ECSReferenceFluid = "R134a";
		};
		virtual ~Fluid();

		// Some post-loading things happen here
		void post_load(void);

		// Fluid-specific parameters
		struct CriticalStruct crit;
		struct FluidLimits limits;
		struct OtherParameters params;
		struct CriticalStruct * preduce; /// A pointer to the point that is used to reduce the T and rho for EOS
		struct CriticalStruct reduce; /// The point that is used to reduce the T and rho for EOS

		

		//// The TTSE lookup tables
		TTSETwoPhaseTableClass TTSESatL;
		TTSETwoPhaseTableClass TTSESatV;
		TTSESinglePhaseTableClass TTSESinglePhase;

		// The class that holds the information on the critical spline parameters
		CriticalSplineStruct_T CriticalSpline_T;

		// Member Access functions
		/// Returns a std::string with the name of the fluid
		std::string get_name(){return name;};
		/// Returns a char* with the name of the fluid
		char * get_namec(){return (char *)name.c_str();};
		std::string get_REFPROPname(){return REFPROPname;};
		std::string get_EOSReference(){return EOSReference;};
		std::string get_TransportReference(){return TransportReference;};
		std::vector<std::string> get_aliases(){return aliases;};
		/// Returns true if the fluid is pure, false if pseudo-pure or a mixture
		bool pure(){return isPure;};
		/// Returns the mass-specific gas constant for the fluid [kJ/kg/K]
		double R(){return params.R_u/params.molemass;};

		// These MUST be implemented by derived class
        virtual double conductivity_Trho(double T, double rho);
		virtual double viscosity_Trho(double T, double rho);
		
		// These Helmholtz energy terms are provided by the base class
		virtual double phir(double tau, double delta);
		// First derivative
		virtual double dphir_dDelta(double tau, double delta);
		virtual double dphir_dTau(double tau, double delta);
		// Second derivative
		virtual double d2phir_dDelta2(double tau, double delta);
		virtual double d2phir_dDelta_dTau(double tau, double delta);
		virtual double d2phir_dTau2(double tau, double delta);
		// Third derivative
		virtual double d3phir_dDelta3(double tau, double delta);
		virtual double d3phir_dDelta2_dTau(double tau, double delta);
		virtual double d3phir_dDelta_dTau2(double tau, double delta);
		virtual double d3phir_dTau3(double tau, double delta);
		
		virtual double phi0(double tau, double delta);
		virtual double dphi0_dDelta(double tau, double delta);
		virtual double dphi0_dTau(double tau, double delta);

		virtual double d2phi0_dDelta2(double tau, double delta);
		virtual double d2phi0_dDelta_dTau(double tau, double delta);
		virtual double d2phi0_dTau2(double tau, double delta);

		virtual double d3phi0_dDelta3(double tau, double delta){throw NotImplementedError();};
		virtual double d3phi0_dDelta2_dTau(double tau, double delta){return 0;};
		virtual double d3phi0_dDelta_dTau2(double tau, double delta){return 0;};
		virtual double d3phi0_dTau3(double tau, double delta);

		// These thermodynamic properties as a function of temperature and density are
		// provided by the base class
		double pressure_Trho(double T, double rho);
		double enthalpy_Trho(double T, double rho);
		double entropy_Trho(double T, double rho);
		double internal_energy_Trho(double T, double rho);
		double speed_sound_Trho(double T, double rho);
		double specific_heat_p_Trho(double T, double rho);
		double specific_heat_p_ideal_Trho(double T);
		double specific_heat_v_Trho(double T, double rho);
		double gibbs_Trho(double T, double rho);
		double dpdT_Trho(double T,double rho);
		double drhodT_p_Trho(double T,double rho);

		// Get the density using the Soave EOS
		double density_Tp_Soave(double T, double p, int iValue = 0);

		virtual double density_Tp(double T, double p);
		virtual double density_Tp(double T, double p, double rho_guess);

		/// Temperature as a function of pressure and entropy
		/// @param h Enthalpy [kJ/kg/K]
		/// @param s Entropy [kJ/kg/K]
		/// @param Tout Temperature [K]
		/// @param rhoout Density [kg/m^3]
		/// @param rhoL Saturated liquid density [kg/m^3]
		/// @param rhoV Saturated vapor density [kg/m^3]
		virtual void temperature_hs(double h, double s, double *Tout, double *rhoout, double *rhoL, double *rhoV, double *TsatLout, double *TsatVout);

		/// Temperature as a function of pressure and entropy
		/// @param p Pressure [kPa]
		/// @param s Entropy [kJ/kg/K]
		/// @param Tout Temperature [K]
		/// @param rhoout Density [kg/m^3]
		/// @param rhoL Saturated liquid density [kg/m^3]
		/// @param rhoV Saturated vapor density [kg/m^3]
		virtual void temperature_ps(double p, double s, double *Tout, double *rhoout, double *rhoL, double *rhoV, double *TsatLout, double *TsatVout);
		
		/// Temperature as a function of pressure and enthalpy
		/// @param p Pressure [kPa]
		/// @param h Enthalpy [kJ/kg]
		/// @param Tout Temperature [K]
		/// @param rhoout Density [kg/m^3]
		/// @param rhoL Saturated liquid density [kg/m^3]
		/// @param rhoV Saturated vapor density [kg/m^3]
		/// @param T0 Starting temperature for the solver
		/// @param rho0 Starting density value for the solver
		virtual void temperature_ph(double p, double h, double *Tout, double *rhoout, double *rhoL, double *rhoV, double *TsatLout, double *TsatVout, double T0 = -1, double rho0 = -1);
		
		double temperature_prho(double p, double rho, double T0);

		double temperature_prho_VanDerWaals(double p, double rho);
		double temperature_prho_PengRobinson(double p, double rho);

		/// Return the phase given the temperature and pressure
		std::string phase_Tp(double T, double p, double *pL, double *pV, double *rhoL, double *rhoV);
		
		/// Return the phase using the phase flags from phase enum in CoolProp.h
		long phase_Tp_indices(double T, double p, double *pL, double *pV, double *rhoL, double *rhoV);
		
		/// Return the phase given the temperature and the density
		std::string phase_Trho(double T, double rho, double *pL, double *pV, double *rhoL, double *rhoV);

		/// Return the phase using the phase flags from phase enum in CoolProp.h
		long phase_Trho_indices(double T, double rho, double *pL, double *pV, double *rhoL, double *rhoV);

		long phase_prho_indices(double p, double rho, double *T, double *TL, double *TV, double *rhoL, double *rhoV);

		// Optional ancillary functions can be overloaded, will throw a NotImplementedError
		// to be caught by calling function if not implemented
		virtual double psat(double T){
			throw NotImplementedError(std::string("psat not implemented for this fluid"));
		};
		virtual double psatL(double T){
			throw NotImplementedError(std::string("psatL not implemented for this fluid"));
		};
		virtual double psatV(double T){
			throw NotImplementedError(std::string("psatV not implemented for this fluid"));
		};
		virtual double rhosatL(double T){
			throw NotImplementedError(std::string("rhosatL not implemented for this fluid"));
		};
		virtual double rhosatV(double T){
			throw NotImplementedError(std::string("rhosatV not implemented for this fluid"));
		};
		double psatL_anc(double T){
			if (isPure)
				return psat(T);
			else
				return psatL(T);
		};
		double psatV_anc(double T){
			if (isPure)
				return psat(T);
			else
				return psatV(T);
		};
		// Ancillary equations composed by interpolating within 3-point 
		// curve that is calculated once
		double hsatV_anc(double T);
		double hsatL_anc(double T);
		double ssatV_anc(double T);
		double ssatL_anc(double T);
		double cpsatV_anc(double T);
		double cpsatL_anc(double T);
		double drhodT_pL_anc(double T);
		double drhodT_pV_anc(double T);
		/// The saturation temperature of the fluid for a given pressure and quality (1 or 0) using only the ancillary equations
		/// @param p Saturation pressure [kPa(abs)]
		/// @param Q Vapor quality in the range [0,1]
		double Tsat_anc(double p, double Q);

		std::vector<double> ConformalTemperature(Fluid *InterestFluid, Fluid *ReferenceFluid,double T, double rho, double T0, double rho0, std::string *errstring);
		// Extended corresponding states functions for fluids that do not have their own high-accuracy
		// transport property implementation
		virtual void ECSParams(double *e_k, double *sigma){
			throw NotImplementedError("ECSParams not implemented for this fluid");
		};
		/// This function is optional, the default value of 1.0 is used otherwise
		///@param rhor The reduced density where rhor = rho/rhoc
		virtual double ECS_psi_viscosity(double rhor){
			return 1.0;
		};
		/// This function is optional, the default value of 1.0 is used otherwise
		///@param rhor The reduced density where rhor = rho/rhoc
		virtual double ECS_chi_conductivity(double rhor){
			return 1.0;
		};
		/// This function is optional, the default value of 1.32e-3 is used otherwise
		///@param T The temperature
		virtual double ECS_f_int(double T){
			return 1.32e-3;
		};
		/// This function is optional, and returns a NotImplementedError if the derived class does not implement it.
		/// Hopefully the calling function catches the error
		///@param T Temperature [K]
		///@param rho Density [kg/m3]
		///@param ReferenceFluid A pointer to an instance of a Fluid class that is used as the reference fluid for the ECS model
		double viscosity_ECS_Trho(double T, double rho, Fluid * ReferenceFluid);

		/// This function is optional, and returns a NotImplementedError if the derived class does not implement it.
		/// Hopefully the calling function catches the error
		///@param T Temperature [K]
		///@param rho Density [kg/m3]
		///@param ReferenceFluid A pointer to an instance of a Fluid class that is used as the reference fluid for the ECS model
		double conductivity_ECS_Trho(double T, double rho, Fluid * ReferenceFluid);

		/// The background viscosity for the fluid.  The viscosity minus the critical contribution minus the dilute-gas contribution
		/// This function is optional, and returns a NotImplementedError if the derived class does not implement it.
		/// Hopefully the calling function catches the error
		/// @see viscosity_Trho
		/// @param T Temperature [K]
		/// @param rho Density [kg/m3]
		virtual double conductivity_background(double T, double rho){
			throw NotImplementedError(std::string("conductivity_background not implemented for this fluid"));
		};

		/// The critical term for the thermal conductivity from Olchowy and Sengers
		/// @param T Temperature [K]
		/// @param rho Density [kg/m^3]
		/// @param qd qd term in term [1/m]
		/// @param GAMMA Gamma term
		/// @param zeta0 zeta0 term in crossover
		double conductivity_critical(double T, double rho, double qd = 2e9, double GAMMA = 0.0496, double zeta0 = 1.94e-10);


		/// This function returns the dilute portion of the viscosity
		/// @param T Temperature [K]
		/// @param e_k epsilon/k_B for the fluid [K]
		/// @param sigma [nm]
		/// @returns mu Dilute-gas viscosity in the limit of zero density [Pa-s]
		double viscosity_dilute(double T, double e_k, double sigma);

		/// The residual viscosity for the fluid.  The sum of the background and critical contributions. 
		/// This function is optional, and returns a NotImplementedError if the derived class does not implement it.
		/// Hopefully the calling function catches the error
		/// @see viscosity_Trho
		/// @param T Temperature [K]
		/// @param rho Density [kg/m3]
		double viscosity_residual(double T, double rho){
			throw NotImplementedError(std::string("viscosity_residual not implemented for this fluid"));
		};
		/// The background viscosity for the fluid.  The viscosity minus the critical contribution minus the dilute-gas contribution
		/// This function is optional, and returns a NotImplementedError if the derived class does not implement it.
		/// Hopefully the calling function catches the error
		/// @see viscosity_Trho
		/// @param T Temperature [K]
		/// @param rho Density [kg/m3]
		virtual double viscosity_background(double T, double rho){
			throw NotImplementedError(std::string("viscosity_background not implemented for this fluid"));
		};

		virtual double surface_tension_T(double T);

		/// Saturation pressure and saturated liquid and vapor densities as a function of the temperature.
		/// @param T Temperature [K]
		/// @param UseLUT If True, use the Saturation Lookup tables, otherwise use the EOS and the equal gibbs function and equal pressure criterion to determine saturation state
		/// @param psatLout Saturated liquid pressure [kPa(abs)]
		/// @param psatVout Saturated vapor pressure [kPa(abs)]
		/// @param rhoLout Saturated liquid density [kg/m3]
		/// @param rhoVout Saturated vapor density [kg/m3]
		virtual void saturation_T(double T, bool UseLUT, double *psatLout, double *psatVout, double *rhoLout, double *rhoVout);

		/// Saturation temperature and saturated liquid and vapor densities as a function of the pressure.
		/// @param p Pressure [kPa(abs)]
		/// @param UseLUT If True, use the Saturation Lookup tables, otherwise use the EOS and the equal gibbs function and equal pressure criterion to determine saturation state
		/// @param TsatLout Saturated liquid temperature [K]
		/// @param TsatVout Saturated vapor temperature [K]
		/// @param rhoLout Saturated liquid density [kg/m3]
		/// @param rhoVout Saturated vapor density [kg/m3]
		virtual void saturation_p(double p, bool UseLUT, double *TsatLout, double *TsatVout, double *rhoLout, double *rhoVout);

		/// Saturation temperature and saturated liquid and vapor densities as a function of the entropy. (The phase must be provided)
		/// @param s Entropy [kJ/kg/K]
		/// @param Q quality [kg/kg]
		/// @param Tsatout Saturated temperature [K]
		/// @param rhoout Saturated density [kg/m3]
		virtual void saturation_s(double s, int Q, double *Tsatout, double *rhoout);
		
		/// NB: Only valid for pure fluids - no pseudo-pure or mixtures.
		/// Get the saturated liquid, vapor densities and the saturated pressure
		/// @param T Temperature [K]]
		/// @param pout Saturated pressure [kPa(abs)]
		/// @param rhoLout Saturated liquid pressure [kg/m3]
		/// @param rhoVout Saturated vapor pressure [kg/m3]
		void rhosatPure(double T, double *rhoLout, double *rhoVout, double *pout);

		/// NB: Only valid for pure fluids - no pseudo-pure or mixtures.
		/// Get the saturated liquid, vapor densities and the saturated pressure using the method from Akasaka given by
		/// Ryo Akasaka, "A reliable and useful Method to Determine the Saturation State from Helmholtz Energy Equations of State", Journal of Thermal Science and Technology, v.3 n3 2008, 442-451
		/// @param T Temperature [K]]
		/// @param pout Saturated pressure [kPa(abs)]
		/// @param rhoLout Saturated liquid pressure [kg/m3]
		/// @param rhoVout Saturated vapor pressure [kg/m3]
		void rhosatPure_Akasaka(double T, double *rhoLout, double *rhoVout, double *pout);

		/// Get the saturated liquid, vapor densities and the saturated pressure using Brent's method and adjusting the pressure
		/// @param T Temperature [K]]
		/// @param pout Saturated pressure [kPa(abs)]
		/// @param rhoLout Saturated liquid pressure [kg/m3]
		/// @param rhoVout Saturated vapor pressure [kg/m3]
		void rhosatPure_Brent(double T, double *rhoLout, double *rhoVout, double *pout);

		/// Get the saturated liquid, vapor densities and the saturated pressure using Brent's method and adjusting the density
		/// @param T Temperature [K]]
		/// @param pout Saturated pressure [kPa(abs)]
		/// @param rhoLout Saturated liquid pressure [kg/m3]
		/// @param rhoVout Saturated vapor pressure [kg/m3]
		void rhosatPure_BrentrhoV(double T, double *rhoLout, double *rhoVout, double *pout);
		
		/// The saturation temperature of the fluid for a given pressure and quality. If the 
		/// fluid is pure, the saturated vapor and saturated liquid temperatures are the same.  
		/// If not, give the "correct" saturation temperature.
		/// @param p Saturation pressure [kPa(abs)]
		/// @param Q Vapor quality in the range [0,1]
		/// @param T_guess  Not currently used due to the use of the Brent solver. Used to be the guess temperature
		double Tsat(double p, double Q, double T_guess);

		/// The saturation temperature of the fluid for a given pressure and quality. If the 
		/// fluid is pure, the saturated vapor and saturated liquid temperatures are the same.  
		/// If not, give the "correct" saturation temperature.
		/// @param p Saturation pressure [kPa(abs)]
		/// @param Q Vapor quality in the range [0,1]
		/// @param T_guess  Not currently used due to the use of the Brent solver. Used to be the guess temperature
		/// @param UseLUT Use the Lookup table (True), or not (False)
		/// @param rhoLout The saturated liquid density [kg/m3]
		/// @param rhoVout The saturated vapor density [kg/m3]
		double Tsat(double p, double Q, double T_guess, bool UseLUT, double *rhoLout, double *rhoVout);
		
		/// Returns true if the given name is an alias of the Fluid name.  (Case-sensitive!!)
		/// @param name The given name
		bool isAlias(std::string name);

		/// Parameters for the Tabular Taylor Series Expansion (TTSE) Method
		bool enabled_TTSE_LUT, built_TTSE_LUT, enable_writing_tables_to_files;

		/// Enable the TTSE
		/// If you want to over-ride parameters, must be done before calling this function
		void enable_TTSE_LUT(void);
		/// Check if TTSE is enabled
		bool isenabled_TTSE_LUT(void);
		/// Disable the TTSE
		void disable_TTSE_LUT(void);
		/// Enable the writing of TTSE tables to file
		void enable_TTSE_LUT_writing(void);
		/// Check if the writing of TTSE tables to file is enabled
		bool isenabled_TTSE_LUT_writing(void);
		/// Disable the writing of TTSE tables to file
		void disable_TTSE_LUT_writing(void);
		/// Over-ride the default size of both of the saturation LUT
		void set_TTSESat_LUT_size(int Nsat);
		/// Over-ride the default size of the single-phase LUT
		void set_TTSESinglePhase_LUT_size(int Np, int Nh);
		/// Over-ride the default range of the single-phase LUT
		void set_TTSESinglePhase_LUT_range(double hmin, double hmax, double pmin, double pmax);
		/// Get the current range of the single-phase LUT
		void get_TTSESinglePhase_LUT_range(double *hmin, double *hmax, double *pmin, double *pmax);
		/// Build of the TTSE LUT
		bool build_TTSE_LUT(bool force = false);
		/// Interpolate within the TTSE LUT
		double interpolate_in_TTSE_LUT(long iParam, long iInput1, double Input1, long iInput2, double Input2);
};

	/// This class contains pointers to all the classes of the fluids that can be used in addition  
	/// to some convenience functions
	class FluidsContainer
	{
	private:
		std::map<std::string,long> fluid_index_map; ///< maps fluid names to 0-based index
		std::map<std::string,Fluid*> fluid_name_map; ///< maps fluid names to pointers to the fluid
		std::vector <Fluid*> FluidsList; ///< A list of pointers to the instances of the fluids
	public:
		/// Constructor for the FluidsContainer class
		/// @see FluidsContainer
		FluidsContainer();

		/// Destructor for the FluidsContainer class.  Deletes each fluid in tern
		/// @see FluidsContainer
		~FluidsContainer();

		/// Accessor.  Throws a NotImplementedError if the fluid given by name is not found.  Also searches aliases
		/// @param name Fluid to be searched for
		Fluid * get_fluid(std::string name);

		/// Accessor.  Throws a NotImplementedError if the fluid index is invalid
		/// @param name Fluid index to be used
		Fluid * get_fluid(long iFluid);

		/// Add a REFPROP fluid to the container
		/// @param FluidName 
		/// @param xmol std::vector of mole fractions - must add to 1
		bool add_REFPROP_fluid(std::string FluidName, std::vector<double> xmol);
		
		/// Get the index of the fluid name
		/// @param pFluid pointer to Fluid instance
		long get_fluid_index(Fluid* pFluid);

		/// Returns a std::string of a comma-separated list of the CoolProp names of all the fluids that are loaded.
		std::string FluidList();
	};

#endif
