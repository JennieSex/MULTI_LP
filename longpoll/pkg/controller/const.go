// Developer: th2empty
// Date: 27.03.2022

package controller

var (
	GetLabAliases           = []string{".п", ".пат", ".патоген"} // get laboratory info
	FindPathogenAliases     = []string{"пп"}                     // search pathogen by name
	FinInfectionsAliases    = []string{".з", ".зз", "зз", "пвк"} // get the user's infection history
	InfectAliases           = []string{"еб", "хуяк"}             // infect one or more users
	EnableAnsweringMachine  = []string{"+ао", "ао+", "ответка+"}
	DisableAnsweringMachine = []string{"-ао", "ао-", "ответка-"}
)
